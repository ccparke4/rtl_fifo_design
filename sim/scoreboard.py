import os

def verify(stim_file="stimulus.txt", resp_file="response.txt", depth=32):
    """
    Sims a golden FIFO model and compares against the HDL version.
    Response format: wclk rst_n winc rinc wfull rempty rdata
    """
    shadow_fifo = []
    expected_outputs = []
    
    if not os.path.exists(stim_file):
        return False, "Stimulus file missing"
    if not os.path.exists(resp_file):
        return False, "Response file missing (sim failed)"

    # Replay the stimulus to build the "expected" list
    with open(stim_file, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4:
                continue
            rst, wr, rd, data = parts[0], parts[1], parts[2], parts[3]
            
            if rst == "1":
                shadow_fifo = []
            else:
                if wr == "1" and len(shadow_fifo) < depth:
                    shadow_fifo.append(data.upper())
                
                if rd == "1" and len(shadow_fifo) > 0:
                    expected_outputs.append(shadow_fifo.pop(0))

    # Parse response file - extract rdata from lines where read occurred
    actual_outputs = []
    with open(resp_file, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 7:
                continue
            # Format: wclk rst_n winc rinc wfull rempty rdata
            rinc   = parts[3]
            rempty = parts[5]
            rdata  = parts[6].upper()
            
            # Only capture output when a valid read happened
            if rinc == "1" and rempty == "0":
                actual_outputs.append(rdata)

    num_expected = len(expected_outputs)
    num_actual = len(actual_outputs)

    if expected_outputs == actual_outputs:
        return True, num_actual
    else:
        print(f"DEBUG: Expected {num_expected} reads, got {num_actual}")
        for i in range(min(num_expected, num_actual)):
            if expected_outputs[i] != actual_outputs[i]:
                print(f"DEBUG: First mismatch at index {i}: Exp {expected_outputs[i]}, Got {actual_outputs[i]}")
                break
        return False, num_actual