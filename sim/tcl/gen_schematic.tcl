# generated schematic from existing checkpoint
set dcp_file [lindex $argv 0]
set output_dir [lindex $argv 1]

if {$dcp_file eq "" || $output_dir eq ""} {
    puts "Usage: vivado -mode batch -source gen_schematic.tcl -tclargs <dcp_file> <output_dir>"
    puts "Example: vivado -mode batch -source gen_schematic.tcl -tclargs post_synth_fifo_sync.dcp ../output/schematics"
    exit 1
}

# Open the checkpoint
open_checkpoint $dcp_file

# Get design name from checkpoint filename
set design_name [file rootname [file tail $dcp_file]]

# Generate schematic
puts "Generating schematic for ${design_name}..."
show_schematic [get_cells -hierarchical]
write_schematic -format pdf -orientation landscape \
    -scope visible -force "${output_dir}/schematic_${design_name}.pdf"

puts "Schematic saved: ${output_dir}/schematic_${design_name}.pdf"