# Synchronous FIFO Design

A parameterizable, synchronous First-In-First-Out (FIFO) memory buffer designed in SystemVerilog. This project features a robust Python-driven verification environment that automates simulation, stimulus generation, and self-checking scoreboard analysis.

## Features
* **Fully Synchronous:** Single clock domain (`clk`).
* **Parameterization:** Easy config. of Data Width and FIFO Depth via parameters.
* **Sell-Checking Scorebaord:** Python acts as a "Golden Model," verifying hardware output against expected behavior automatically.
* **Sticky Error Handling:** "Sticky" `overflow` and `underflow` flags that latch High upon error and remain asserted until reset. This ensures that even transient errors are captured and not missed by the controlling logic.
* **Automated Regression:** `run_regression.py` handles compilation, elaboration, and simulation.

## Project Structure
* **`rtl/fifo_sync.sv`**: SystemVerilog design containing logic, memory array, and sticky error flags.
* **`tb/tb_fifo.sv`**: SystemVerilog testbench. It reads `stimulus.txt` (via Python) and writes `response.txt`.
* **`sim/run_regression.py`**: Automation controller. Compiles the design, runs Vivado in batch mode, and triggers the scoreboard.
* **`sim/scoreboard.py`**: A python script that parses the simulation output and validates data. (PASS/FAIL).
* **`sim/xsim_cfg.tcl`**: TCL commands for Vivado batch mode execution.

## Interface

| Port Name | Direction | Width | Description |
| :--- | :--- | :--- | :--- |
| `clk` | Input | 1-bit | System Clock. |
| `rst` | Input | 1-bit | Active High Reset. Clears pointers and flags. |
| `wr_en` | Input | 1-bit | Write Enable. Writes `data_in` on rising edge if not full. |
| `rd_en` | Input | 1-bit | Read Enable. Reads to `data_out` on rising edge if not empty. |
| `data_in` | Input | `[DATA_WIDTH-1:0]` | Data input bus. |
| `data_out` | Output | `[DATA_WIDTH-1:0]` | Data output bus. |
| `full` | Output | 1-bit | Asserted when FIFO memory is full. |
| `empty` | Output | 1-bit | Asserted when FIFO memory is empty. |
| `overflow` | Output | 1-bit | **Sticky Flag.** Goes High if a write is attempted while Full. |
| `underflow`| Output | 1-bit | **Sticky Flag.** Goes High if a read is attempted while Empty. |

## ⚙️ Parameters (Default)
* **`DATA_WIDTH`**: `8` (8-bit data)
* **`ADDR_WIDTH`**: `5` (Defines depth as $2^5 = 32$ words)

## Verification Flow

This project uses a Python wrapper around the hardware simulation:
1. **Stimulus Generation:** Python generates random read/write transactions (`stimulus.txt`).
2. **Hardware Simulation:** Vivado (xsim) runs the SystemVerilog testbench, which consumes the stimulus and produces `response.txt`.
3. **Scoreboard Check:** Python reads `response.txt`, mimics the FIFO ligc in the software, and compares results.

## How to Run
### Requirements
* Xilinx Vivado
* Python 3.x

### Steps

1. Open a terminal `sim/` directory: `cd sim`
2. Run regression script: `python run_regression.py`
3. Check Results:
  * Terminal will display `PASS: ...`
  * To view waveforms, open the genereated `topsim.wdb` in Vivado.

## Future Work & Next Steps
* **Synthesis & Timing:** Run Vivado Synthesis to analyze resource utilization (LUT/FF count) and verify timing constraints.
* **Asynchronous Implementation:** Adapt the design to use Gray Code pointers for safe data transfer between different clock domains (CDC).
* **AXI4-Stream Interface:** Wrap the core logic in an AXI wrapper for standard integration with Xilinx IP blocks (Zynq/MicroBlaze).
