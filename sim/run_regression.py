import subprocess
import glob
import os
import scoreboard
from tests import test_library

VIVADO_PATH = r"C:\\AMDDesignTools\\2025.2\\Vivado\\bin"
if VIVADO_PATH not in os.environ["PATH"]:
    os.environ["PATH"] = VIVADO_PATH + os.pathsep + os.environ["PATH"]

def run_vivado_sim():
    cleanup_logs()

    print("Step 1: Compiling...")
    # Compile RTL and TB
    subprocess.run("xvlog -sv ../rtl/fifo_sync.sv ../tb/tb_fifo.sv", shell=True, check=True)
   
    print("Step 2: Elaborating...")
    # Creates the 'topsim' executable snapshot
    subprocess.run("xelab -debug typical tb_fifo -s topsim", shell=True, check=True)

    print("Step 3: Simulating...")
    # -tclbatch xsim_cfg.tcl logs the waveforms
    subprocess.run("xsim topsim -tclbatch xsim_cfg.tcl -onerror quit", shell=True, check=True)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("=== Starting FIFO Test Suite ===")

    with open("stimulus.txt", "w") as f:
        print("Generating Burst Test...")
        test_library.gen_simultaneous_burst(f)

    try:
        run_vivado_sim()
    except Exception as e:
        print(f"Vivado Error: {e}")
        return

    print("Checking Scoreboard...")
    passed, count = scoreboard.verify()
    
    if passed:
        print(f"PASS: {count} transactions verified!")
    else:
        print("FAIL: Data mismatch detected.")


def cleanup_logs():
    print("Cleaning up old Vivado logs...")
    # List of extensions to delete
    patterns = ['*.log', '*.jou', '*.pb', 'xsim.dir']
    for pattern in patterns:
        for f in glob.glob(pattern):
            try:
                if os.path.isdir(f):
                    import shutil
                    shutil.rmtree(f)
                else:
                    os.remove(f)
            except:
                continue

if __name__ == "__main__":
    main()