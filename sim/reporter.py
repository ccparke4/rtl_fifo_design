import matplotlib.pyplot as plt
import os

def generate_charts(results):
    """
    Creates a Bar Chart comparing LUTs and Registers usage.
    Saves it as 'comparison_plot.png'.
    """
    names = [r['name'] for r in results]
    
    # Safely convert to int, default to 0 if synthesis failed ('-')
    luts = [int(r['luts']) if r['luts'].isdigit() else 0 for r in results]
    regs = [int(r['regs']) if r['regs'].isdigit() else 0 for r in results]

    x = range(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bar1 = ax.bar([i - width/2 for i in x], luts, width, label='LUTs (Logic)', color='#1f77b4')
    bar2 = ax.bar([i + width/2 for i in x], regs, width, label='FFs (Memory)', color='#ff7f0e')

    ax.set_ylabel('Count')
    ax.set_title('FPGA Resource Utilization: Sync vs Async FIFO')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()

    # Add text labels on bars
    ax.bar_label(bar1, padding=3)
    ax.bar_label(bar2, padding=3)

    plt.tight_layout()
    plt.savefig('comparison_plot.png')
    print("Generated Chart: comparison_plot.png")

def generate_markdown(results):
    """
    Generates a README-style report summarizing the run.
    """
    with open("REPORT.md", "w") as f:
        f.write("# FIFO Design Comparison Report\n\n")
        f.write("## 1. Simulation Status\n")
        f.write("| Design | Status | Notes |\n")
        f.write("| :--- | :--- | :--- |\n")
        for r in results:
            note = "Pass" if r['sim'] == "PASS" else "**FAIL**"
            f.write(f"| {r['name']} | {r['sim']} | {note} |\n")
        
        f.write("\n## 2. Resource Utilization\n")
        f.write("![Comparison Plot](comparison_plot.png)\n\n")
        
        f.write("| Design | LUTs | Flip-Flops |\n")
        f.write("| :--- | :--- | :--- |\n")
        for r in results:
            f.write(f"| {r['name']} | {r['luts']} | {r['regs']} |\n")

        f.write("\n## 3. Schematic Artifacts\n")
        f.write("The synthesized schematics have been generated as PDFs:\n")
        f.write("* [Sync FIFO Schematic](schematic_fifo_sync_top.pdf)\n")
        f.write("* [Async FIFO Schematic](schematic_async_fifo.pdf)\n")

    print("Generated Report: REPORT.md")