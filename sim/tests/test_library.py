import random

def gen_empty_stress(f, depth=32):
    """ Checks if the FIFO handles a 'Read-while-empty' correctly."""
    # reset
    f.write("1 0 0 00\n")
    f.write("0 0 0 00\n")
    # attempt 50 rds on an empty FIFO
    for _ in range(50):
        f.write("0 0 1 00\n")
    
    # then write one value and read it to ensure it works
    f.write("0 1 0 AA\n")
    f.write("0 0 1 00\n")

def gen_full_stress(f, depth=32):
    """Checks if the FIFO handles a 'Write-while-Full' correctly."""
    f.write("1 0 0 00\n")
    f.write("0 0 0 00\n")
    # Fill it
    for i in range(depth):
        f.write(f"0 1 0 {i:02X}\n")
    # Attempt 50 more writes
    for _ in range(50):
        f.write("0 1 0 FF\n")
    # Empty it
    for _ in range(depth):
        f.write("0 0 1 00\n")

def gen_simultaneous_burst(f, depth=32):
    """Stress tests simultaneous Read and Write (High Bandwidth)."""
    f.write("1 0 0 00\n")
    f.write("0 0 0 00\n")
    # Fill halfway
    for i in range(depth // 2):
        f.write(f"0 1 0 {i:02X}\n")
    # 100 cycles of both WR and RD active
    for i in range(100):
        f.write(f"0 1 1 {random.randint(0,255):02X}\n")