# get args
set rtl_file [lindex $argv 0]
set top_module [lindex $argv 1]
set part_name "xc7a35tcpg236-1"

read_verilog -sv $rtl_file
synth_design -top $top_module -part $part_name -mode out_of_context

report_utilization -file "utilization.rpt"

create_clock -name sys_clk -period 10.0 [get_ports *clk*]
report_timing_summary -file "timing.rpt"
