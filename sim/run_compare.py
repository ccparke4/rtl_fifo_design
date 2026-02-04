import subprocess
import os
import re
import sys
import argparse

# Add parent paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import scoreboard
import reporter
from tests import test_library

# --- CONFIG ---
VIVADO_BIN = r"C:\AMDDesignTools\2025.2\Vivado\bin" 
if VIVADO_BIN not in os.environ["PATH"]:
    os.environ["PATH"] = VIVADO_BIN + os.pathsep + os.environ["PATH"]

# Paths relative to sim/ directory
PATHS = {
    "rtl": "../rtl",
    "tb": "../tb",
    "tcl": "tcl",
    "output": "../output",
    "reports": "../output/reports",
    "schematics": "../output/schematics",
}

DESIGNS = [
    {
        "name": "Sync FIFO",
        "rtl": f"{PATHS['rtl']}/fifo_sync.sv",
        "tb": f"{PATHS['tb']}/tb_fifo_unified.sv",
        "sim_top": "tb_fifo_unified",
        "synth_top": "fifo_sync_top",
        "flags": ""
    },
    {
        "name": "Async FIFO",
        "rtl": f"{PATHS['rtl']}/fifo_async.sv",
        "tb": f"{PATHS['tb']}/tb_fifo_unified.sv",
        "sim_top": "tb_fifo_unified",
        "synth_top": "async_fifo",
        "flags": "-d ASYNC_MODE"
    }
]

def parse_args():
    parser = argparse.ArgumentParser(description="FIFO Verification & Synthesis Suite")
    parser.add_argument("--schematic", "-s", action="store_true",
                        help="Generate schematic PDFs after synthesis")
    parser.add_argument("--waveform", "-w", action="store_true",
                        help="Open waveform viewer after simulation")
    parser.add_argument("--gui", "-g", action="store_true",
                        help="Open Vivado GUI after synthesis for interactive exploration")
    parser.add_argument("--design", "-d", choices=["sync", "async", "all"], default="all",
                        help="Which design to run (default: all)")
    parser.add_argument("--sim-only", action="store_true",
                        help="Run simulation only, skip synthesis")
    parser.add_argument("--synth-only", action="store_true",
                        help="Run synthesis only, skip simulation")
    return parser.parse_args()

def open_vivado_gui(design):
    """Open Vivado GUI for interactive schematic exploration."""
    dcp_file = f"{PATHS['reports']}/post_synth_{design['synth_top']}.dcp"
    
    if not os.path.exists(dcp_file):
        print(f"  [X] Checkpoint not found: {dcp_file}")
        return
    
    print(f"\n  Opening Vivado GUI for {design['name']}...")
    print(f"  (Close Vivado to continue)")
    
    cmd = f"vivado -mode gui -source {PATHS['tcl']}/open_gui.tcl -tclargs {dcp_file}"
    subprocess.run(cmd, shell=True)

def ensure_output_dirs():
    """Create output directories if they don't exist."""
    for key in ["output", "reports", "schematics"]:
        os.makedirs(PATHS[key], exist_ok=True)

def print_log_tail(logfile, lines=20):
    if os.path.exists(logfile):
        print(f"\n--- TAIL of {logfile} ---")
        with open(logfile, 'r') as f:
            for line in f.readlines()[-lines:]:
                print(line.strip())
        print("----------------------------\n")

def run_simulation(design, open_waveform=False):
    print(f"\n{'='*60}")
    print(f"  SIMULATING: {design['name']}")
    print(f"{'='*60}")
    
    with open("stimulus.txt", "w") as f:
        test_library.gen_simultaneous_burst(f)

    cmd_compile = f"xvlog -sv {design['flags']} {design['rtl']} {design['tb']}"
    cmd_elab = f"xelab -debug typical {design['sim_top']} -s topsim"

    try:
        subprocess.run(cmd_compile, shell=True, check=True)
        subprocess.run(cmd_elab, shell=True, check=True)
        
        with open("xsim_cfg.tcl", "w") as f:
            f.write("log_wave -recursive *\n")
            f.write("run all\nquit\n")

        subprocess.run("xsim topsim -tclbatch xsim_cfg.tcl -onerror quit", 
                      shell=True, check=True)
        
        passed, count = scoreboard.verify()
        status = "PASS" if passed else "FAIL"
        
        print(f"\n  Result: {status} ({count} transactions)")
        if not passed:
            print(f"  WARNING: MISMATCH DETECTED - check DEBUG output above")
        
        # Open waveform viewer if requested
        if open_waveform:
            wdb_file = "topsim.wdb"
            if os.path.exists(wdb_file):
                print(f"\n  Opening waveform viewer for {design['name']}...")
                print(f"  (Close the viewer to continue)")
                subprocess.run(f"xsim {wdb_file} -gui", shell=True)
            else:
                print(f"  WARNING: Waveform file not found: {wdb_file}")
        
        return {"status": status, "transactions": count}

    except subprocess.CalledProcessError:
        print(f"  [X] Simulation CRASHED")
        print_log_tail("xelab.log")
        return {"status": "ERROR", "transactions": 0}

def run_synthesis(design, gen_schematic=False):
    print(f"\n{'='*60}")
    print(f"  SYNTHESIZING: {design['name']}")
    print(f"{'='*60}")
    
    if os.path.exists("vivado.log"):
        os.remove("vivado.log")

    schematic_flag = "1" if gen_schematic else "0"
    schematic_dir = os.path.abspath(PATHS['schematics'])
    reports_dir = os.path.abspath(PATHS['reports'])
    
    cmd = (f"vivado -mode batch -source {PATHS['tcl']}/synth.tcl "
           f"-tclargs {design['rtl']} {design['synth_top']} {schematic_flag} "
           f"{reports_dir} {schematic_dir}")
    
    try:
        with open("vivado.log", "w") as log_file:
            subprocess.run(cmd, shell=True, check=True, 
                          stdout=log_file, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print(f"  [X] Synthesis FAILED")
        print_log_tail("vivado.log", lines=30)
        return {"lut_logic": "-", "lut_mem": "-", "ffs": "-", "wns": "-", "whs": "-", "schematic": "-"}
    
    results = {
        "lut_logic": "N/A", 
        "lut_mem": "N/A", 
        "ffs": "N/A", 
        "wns": "N/A",
        "whs": "N/A",
        "schematic": "-"
    }
    
    # Parse utilization
    util_rpt = f"{PATHS['reports']}/utilization_{design['synth_top']}.rpt"
    if os.path.exists(util_rpt):
        with open(util_rpt, "r") as f:
            content = f.read()
            
            match = re.search(r"LUT as Logic\s*\|\s*(\d+)", content)
            if match: results["lut_logic"] = match.group(1)
            
            match = re.search(r"LUT as Memory\s*\|\s*(\d+)", content)
            if match: results["lut_mem"] = match.group(1)
            
            match = re.search(r"Slice Registers\s*\|\s*(\d+)", content)
            if match: results["ffs"] = match.group(1)
    
    # Parse timing
    timing_rpt = f"{PATHS['reports']}/timing_{design['synth_top']}.rpt"
    if os.path.exists(timing_rpt):
        with open(timing_rpt, "r") as f:
            content = f.read()
            
            # Match the Design Timing Summary table
            match = re.search(
                r"WNS\(ns\)\s+TNS\(ns\).*?\n"    # Header
                r"\s*-+.*?\n"                     # Dashes
                r"\s*(-?[\d.]+)\s+"               # WNS
                r"(-?[\d.]+)\s+"                  # TNS
                r"\d+\s+\d+\s+"                   # TNS endpoints
                r"(-?[\d.]+)",                    # WHS
                content,
                re.DOTALL
            )
            if match:
                results["wns"] = match.group(1)
                results["whs"] = match.group(3)
    
    # Check for schematic
    schematic_file = f"{PATHS['schematics']}/schematic_{design['synth_top']}.pdf"
    if os.path.exists(schematic_file):
        results["schematic"] = schematic_file
        print(f"  Schematic: {schematic_file}")
    
    print(f"  LUT Logic: {results['lut_logic']}, LUT Mem: {results['lut_mem']}, "
          f"FFs: {results['ffs']}, WNS: {results['wns']}ns, WHS: {results['whs']}ns")
    
    return results

def main():
    args = parse_args()
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Working Directory: {os.getcwd()}")
    
    # Create output directories
    ensure_output_dirs()
    
    # Filter designs based on argument
    if args.design == "sync":
        designs_to_run = [d for d in DESIGNS if "Sync" in d['name']]
    elif args.design == "async":
        designs_to_run = [d for d in DESIGNS if "Async" in d['name']]
    else:
        designs_to_run = DESIGNS
    
    results = {d['name']: {'design': d} for d in designs_to_run}

    # =========================================================================
    # PHASE 1: Simulations
    # =========================================================================
    if not args.synth_only:
        print("\n" + "#"*60)
        print("#" + " PHASE 1: FUNCTIONAL SIMULATION ".center(58) + "#")
        print("#"*60)
        
        for name, data in results.items():
            sim_result = run_simulation(data['design'], open_waveform=args.waveform)
            data['sim'] = sim_result
        
        # Summary after all sims
        print("\n" + "-"*60)
        print("SIMULATION SUMMARY:")
        for name, data in results.items():
            status = data['sim']['status']
            symbol = "[OK]" if status == "PASS" else "[FAIL]"
            print(f"  {symbol} {name}: {status} ({data['sim']['transactions']} txns)")
        print("-"*60)
    else:
        for name, data in results.items():
            data['sim'] = {"status": "SKIPPED", "transactions": 0}

    # =========================================================================
    # PHASE 2: Synthesis
    # =========================================================================
    if not args.sim_only:
        print("\n" + "#"*60)
        print("#" + " PHASE 2: SYNTHESIS & RESOURCE ANALYSIS ".center(58) + "#")
        print("#"*60)
        
        for name, data in results.items():
            if data['sim']['status'] != "ERROR":
                data['synth'] = run_synthesis(data['design'], gen_schematic=args.schematic)
                
                # Open GUI if requested
                if args.gui:
                    open_vivado_gui(data['design'])
            else:
                data['synth'] = {"lut_logic": "-", "lut_mem": "-", "ffs": "-", "wns": "-", "whs": "-", "schematic": "-"}
    else:
        # --sim-only: set placeholder synth results
        for name, data in results.items():
            data['synth'] = {"lut_logic": "-", "lut_mem": "-", "ffs": "-", "wns": "-", "whs": "-", "schematic": "-"}

    # =========================================================================
    # FINAL REPORT
    # =========================================================================
    print("\n" + "="*90)
    print(" FINAL COMPARISON REPORT ".center(90, "="))
    print("="*90)
    print(f"{'DESIGN':<15} | {'SIM':<6} | {'LUT Logic':<10} | {'LUT Mem':<8} | {'FFs':<6} | {'WNS(ns)':<8} | {'WHS(ns)':<8}")
    print("-"*90)
    for name, data in results.items():
        s = data['synth']
        print(f"{name:<15} | {data['sim']['status']:<6} | {s['lut_logic']:<10} | "
              f"{s['lut_mem']:<8} | {s['ffs']:<6} | {s['wns']:<8} | {s['whs']:<8}")
    print("="*90)
    
    # List generated schematics
    if args.schematic:
        print("\nGenerated Schematics:")
        for name, data in results.items():
            sch = data['synth'].get('schematic', '-')
            if sch != '-':
                print(f"  - {sch}")

    # Generate artifacts
    print("\nGenerating Report Artifacts...")
    try:
        flat_results = [{
            "name": name,
            "sim": data['sim']['status'],
            "lut_logic": data['synth']['lut_logic'],
            "lut_mem": data['synth']['lut_mem'],
            "ffs": data['synth']['ffs'],
            "wns": data['synth']['wns'],
            "whs": data['synth']['whs']
        } for name, data in results.items()]
        
        reporter.generate_charts(flat_results, PATHS['reports'])
        reporter.generate_markdown(flat_results, PATHS['reports'])
    except Exception as e:
        print(f"Failed to generate report: {e}")

if __name__ == "__main__":
    main()