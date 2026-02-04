# Arguments: rtl_file top_module gen_schematic reports_dir schematics_dir
set rtl_file [lindex $argv 0]
set top_module [lindex $argv 1]
set gen_schematic [lindex $argv 2]
set reports_dir [lindex $argv 3]
set schematics_dir [lindex $argv 4]

set part_name "xc7a35tcpg236-1"

# Read and synthesize
read_verilog -sv $rtl_file
synth_design -top $top_module -part $part_name -mode out_of_context

# Save checkpoint for later GUI/schematic use
write_checkpoint -force "${reports_dir}/post_synth_${top_module}.dcp"

# Generate reports with unique names
report_utilization -file "${reports_dir}/utilization_${top_module}.rpt"

# Create clock and timing report
create_clock -name sys_clk -period 10.0 [get_ports *clk*]
report_timing_summary -file "${reports_dir}/timing_${top_module}.rpt"

# Optional schematic generation
if {$gen_schematic eq "1"} {
    puts "Generating schematic PDF..."
    show_schematic [get_cells -hierarchical]
    write_schematic -format pdf -orientation landscape \
        -scope visible -force "${schematics_dir}/schematic_${top_module}.pdf"
    puts "Schematic saved to: ${schematics_dir}/schematic_${top_module}.pdf"
}

puts "Synthesis complete for ${top_module}"