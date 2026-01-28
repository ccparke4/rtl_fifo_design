import os

def verify(stim_file="stimulus.txt", resp_file="response.txt", depth=32):
    """
    sims a golden FIFO model and compares against the HDL version
    """
    shadow_fifo = []
    expected_outputs = []

    if not os.path.exists(stim_file):
        return False, "Stimulus file missing"
    if not os.path.exists(resp_file):
        return False, "Response file missing (sim failed)"

    # Replay the stimuls to build the "expected" list
    with open(stim_file, "r") as f:
        for line in f:
            parts = line.split()
            if not parts: continue

            rst, wr, rd, data = parts

            if rst == "1":
                shadow_fifo = []
            else:
                # golden write logic
                if wr == "1" and len(shadow_fifo) < depth:
                    shadow_fifo.append(data)
                
                # Golden read logic
                if rd == "1" and len(shadow_fifo) > 0:
                    expected_outputs.append(shadow_fifo.pop(0))

    # read the actual response
    with open(resp_file, "r") as f:
        actual_outputs = [line.strip().upper() for line in f.readlines() if line.strip()]

    num_expected = len(expected_outputs)
    num_actual = len(actual_outputs)

    if expected_outputs == actual_outputs:
        return True, num_actual
    else:
        print(f"DEBUG: Expected {num_expected} reads, but got {num_actual}")
        # find first mismatch
        for i in range(min(num_expected, num_actual)):
            if expected_outputs[i] != actual_outputs[i]:
                print(f"DEBUG: First mismatch at index {i}: Exp {expected_outputs[i]}, Got {actual_outputs[i]}")
                break
        return False, num_actual
    