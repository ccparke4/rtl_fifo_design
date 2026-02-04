import matplotlib.pyplot as plt
import os

def generate_charts(results, output_dir="."):
    """
    Creates a Bar Chart comparing LUTs and Registers usage.
    """
    names = [r['name'] for r in results]
    
    # Safely convert to int, default to 0 if synthesis failed
    def safe_int(val):
        if isinstance(val, str) and val.isdigit():
            return int(val)
        return 0
    
    lut_logic = [safe_int(r.get('lut_logic', 0)) for r in results]
    lut_mem = [safe_int(r.get('lut_mem', 0)) for r in results]
    ffs = [safe_int(r.get('ffs', 0)) for r in results]
    
    x = range(len(names))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bar1 = ax.bar([i - width for i in x], lut_logic, width, label='LUT as Logic', color='#1f77b4')
    bar2 = ax.bar([i for i in x], lut_mem, width, label='LUT as Memory', color='#2ca02c')
    bar3 = ax.bar([i + width for i in x], ffs, width, label='Flip-Flops', color='#ff7f0e')
    
    ax.set_ylabel('Count')
    ax.set_title('FPGA Resource Utilization: Sync vs Async FIFO')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    
    ax.bar_label(bar1, padding=3)
    ax.bar_label(bar2, padding=3)
    ax.bar_label(bar3, padding=3)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'comparison_plot.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Generated Chart: {output_path}")

def generate_markdown(results, output_dir="."):
    output_path = os.path.join(output_dir, "REPORT.md")
    
    with open(output_path, "w") as f:
        f.write("# FIFO Design Comparison Report\n\n")
        
        f.write("## 1. Simulation Status\n\n")
        f.write("| Design | Status |\n")
        f.write("| :--- | :--- |\n")
        for r in results:
            status_icon = "PASS" if r['sim'] == "PASS" else "**FAIL**"
            f.write(f"| {r['name']} | {status_icon} |\n")
        
        f.write("\n## 2. Resource Utilization\n\n")
        f.write("![Comparison Plot](comparison_plot.png)\n\n")
        
        f.write("| Design | LUT Logic | LUT Memory | Flip-Flops | WNS (ns) | WHS (ns) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for r in results:
            f.write(f"| {r['name']} | {r.get('lut_logic', 'N/A')} | "
                    f"{r.get('lut_mem', 'N/A')} | {r.get('ffs', 'N/A')} | "
                    f"{r.get('wns', 'N/A')} | {r.get('whs', 'N/A')} |\n")
        
        f.write("\n## 3. Analysis\n\n")
        f.write("### Resource Comparison\n\n")
        f.write("- **LUT as Logic**: Combinational logic (pointer math, comparators)\n")
        f.write("- **LUT as Memory**: Distributed RAM for FIFO storage\n")
        f.write("- **Flip-Flops**: Sequential elements (pointers, synchronizers)\n")
        f.write("- **WNS**: Worst Negative Slack (setup timing margin)\n")
        f.write("- **WHS**: Worst Hold Slack (hold timing margin)\n")
    
    print(f"Generated Report: {output_path}")