set dcp_file [lindex $argv 0]

if {$dcp_file eq ""} {
    puts "Usage: vivado -mode gui -source open_gui.tcl -tclargs <dcp_file>"
    puts "Example: vivado -mode gui -source open_gui.tcl -tclargs post_synth_fifo_sync.dcp"
    exit 1
}

# Open the checkpoint
open_checkpoint $dcp_file

# Start the GUI
start_gui