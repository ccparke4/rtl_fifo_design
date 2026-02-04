import subprocess
import os
import re
import sys

import reporter

# Ensure we can find the local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import scoreboard
from tests import test_library

# --- CONFIG ---
VIVADO_BIN = r"C:\AMDDesignTools\2025.2\Vivado\bin" 
if VIVADO_BIN not in os.environ["PATH"]:
    os.environ["PATH"] = VIVADO_BIN + os.pathsep + os.environ["PATH"]

DESIGNS = [
    {
        "name": "Sync FIFO",
        "rtl": "../rtl/fifo_sync.sv",
        "tb": "../tb/tb_fifo_unified.sv",
        "sim_top": "tb_fifo_unified",      # For xelab
        "synth_top": "fifo_sync_top",      # For Vivado  ← ADD THIS
        "flags": ""
    },
    {
        "name": "Async FIFO",
        "rtl": "../rtl/fifo_async.sv",
        "tb": "../tb/tb_fifo_unified.sv",
        "sim_top": "tb_fifo_unified",
        "synth_top": "async_fifo",         # ← ADD THIS
        "flags": "-d ASYNC_MODE"
    }
]

def print_log_tail(logfile, lines=20):
    """Helper to print last N lines of a log file."""
    if os.path.exists(logfile):
        print(f"\n--- TAIL of {logfile} ---")
        with open(logfile, 'r') as f:
            content = f.readlines()
            for line in content[-lines:]:
                print(line.strip())
        print("----------------------------\n")

def run_simulation(design):
    print(f"\n--- Simulating {design['name']} ---")
    
    # 1. Generate Stimulus
    with open("stimulus.txt", "w") as f:
        test_library.gen_simultaneous_burst(f)

    # 2. Compile & Elaborate
    cmd_compile = f"xvlog -sv {design['flags']} {design['rtl']} {design['tb']}"
    cmd_elab = f"xelab -debug typical {design['sim_top']} -s topsim"

    try:
        subprocess.run(cmd_compile, shell=True, check=True)
        subprocess.run(cmd_elab, shell=True, check=True)
        
        # 3. Run Sim (With Waveform Logging enabled)
        # We write a specific TCL config for this run
        with open("xsim_cfg.tcl", "w") as f:
            f.write("log_wave -recursive *\n")  # <--- THIS ENABLES WAVEFORMS
            f.write("run all\nquit\n")

        cmd_sim = "xsim topsim -tclbatch xsim_cfg.tcl -onerror quit"
        subprocess.run(cmd_sim, shell=True, check=True)
        
        # 4. Scoreboard
        passed, count = scoreboard.verify()
        
        # --- PRINT SUMMARY FOR THIS TEST ---
        status = "PASS" if passed else "FAIL"
        print(f"\n{'='*50}")
        print(f"  {design['name']} SIMULATION SUMMARY")
        print(f"{'='*50}")
        print(f"  Status:      {status}")
        print(f"  Transactions: {count}")
        if passed:
            print(f"  Result:      All {count} reads matched expected values")
        else:
            print(f"  Result:      MISMATCH DETECTED - check DEBUG output above")
        print(f"{'='*50}\n")
        
        return status

    except subprocess.CalledProcessError:
        print(f"!!! Simulation Failed for {design['name']} !!!")
        print_log_tail("xelab.log") # Try to show why
        return "ERROR"

def run_synthesis(design):
    print(f"--- Synthesizing {design['name']} (Measuring Area & Timing) ---")
    
    # Clean previous log
    if os.path.exists("vivado.log"): os.remove("vivado.log")

    cmd = f"vivado -mode batch -source synth.tcl -tclargs {design['rtl']} {design['synth_top']}"
    
    try:
        # We capture output to file so we can print it on error
        with open("vivado.log", "w") as log_file:
            subprocess.run(cmd, shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print(f"!!! Synthesis Failed for {design['name']} !!!")
        print_log_tail("vivado.log", lines=30) # Show the error!
        return "-", "-"
    
    # Parse Results
    luts = "N/A"
    regs = "N/A"
    if os.path.exists("utilization.rpt"):
        with open("utilization.rpt", "r") as f:
            content = f.read()
            lut_match = re.search(r"LUT\s+as\s+Logic\s*\|\s*(\d+)", content)
            reg_match = re.search(r"Slice Registers\s*\|\s*(\d+)", content)
            if lut_match: luts = lut_match.group(1)
            if reg_match: regs = reg_match.group(1)
            
    return luts, regs

def main():
    # Set CWD to script location
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Working Directory: {os.getcwd()}")

    results = []

    print("=== STARTING FIFO COMPARISON SUITE ===")

    for d in DESIGNS:
        sim_status = run_simulation(d)
        
        # Only run synthesis if simulation didn't crash
        if sim_status != "ERROR":
            luts, regs = run_synthesis(d)
        else:
            luts, regs = "-", "-"
        
        results.append({
            "name": d['name'],
            "sim": sim_status,
            "luts": luts,
            "regs": regs
        })

    # --- PRINT COMPARISON TABLE ---
    print("\n" + "="*60)
    print(f"{'DESIGN':<15} | {'SIM':<10} | {'LUTs (Logic)':<12} | {'FFs (Memory)':<12}")
    print("-" * 60)
    for r in results:
        print(f"{r['name']:<15} | {r['sim']:<10} | {r['luts']:<12} | {r['regs']:<12}")
    print("="*60)

    print("\nGenerating Report Artifacts...")
    try:
        reporter.generate_charts(results)
        reporter.generate_markdown(results)
    except Exception as e:
        print(f"Failed to generate report: {e}")

if __name__ == "__main__":
    main()