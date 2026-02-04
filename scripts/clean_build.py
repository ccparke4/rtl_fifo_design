import os
import shutil
import glob

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # fpga/
DIRS_TO_REMOVE = [
    "sim/xsim.dir",
    "sim/.Xil",
    "FIFO/FIFO.cache",
    "FIFO/FIFO.hw",
    "FIFO/FIFO.sim",
    "FIFO/FIFO.ip_user_files",
    "sim/tests/__pycache__",
    "sim/__pycache__"
]

FILES_TO_REMOVE = [
    "*.log",
    "*.jou",
    "*.pb",
    "*.str",
    "docs/*.txt",
    "docs/*.log",
    "sim/*.log",
    "sim/*.pb",
    "sim/*.jou",
    "sim/*.wdb",       
    "sim/*.str",
    "sim/response.txt",
    "sim/stimulus.txt",
    "sim/dfx_runtime.txt",
    "FIFO/*.log",
    "FIFO/*.jou"
]

def remove_directory(dir_path):
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            print(f"   [DIR] Deleted: {dir_path}")
        except Exception as e:
            print(f"   [ERR] Could not delete {dir_path}: {e}")

def remove_files_by_pattern(pattern):
    for filepath in glob.glob(pattern, recursive=True):
        try:
            os.remove(filepath)
            print(f"   [FILE] Deleted: {filepath}")
        except Exception as e:
            print(f"   [ERR] Could not delete {filepath}: {e}")

def clean_python_cache():
    """Recursively find and delete all __pycache__ folders"""
    print("   [PY] Scanning for __pycache__...")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            path = os.path.join(root, "__pycache__")
            remove_directory(path)
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))

def main():
    print("=== Starting Project Cleanup ===")
    
    # 1. Clean defined directories
    for folder in DIRS_TO_REMOVE:
        remove_directory(folder)

    # 2. Clean defined file patterns
    for pattern in FILES_TO_REMOVE:
        remove_files_by_pattern(pattern)

    # 3. Deep clean Python cache
    clean_python_cache()
    
    print("\n=== Cleanup Complete ===")
    print("Project is clean. Ready for Git or a fresh build.")

if __name__ == "__main__":
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir("..")
        
    main()