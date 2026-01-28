`timescale 1ns / 1ps

module tb_fifo;
    // match to RTL params
    localparam int DATA_WIDTH = 8;
    localparam int ADDR_WIDTH = 5;

    // signals connecting to fifo
    logic clk;
    logic rst;
    logic wr_en;
    logic rd_en;
    logic [DATA_WIDTH-1:0] data_in;
    logic [DATA_WIDTH-1:0] data_out;
    logic full;
    logic empty;
    logic overflow;
    logic underflow;

    // File handling
    int in_file, out_file, status;

    // Instantiate fifo
    fifo_sync_top #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) sFifo_DUT (.*);   // connect automatically
    
    // clock gen - 100MHz
    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        // open files for python 
        in_file  = $fopen("stimulus.txt", "r");
        out_file = $fopen("response.txt", "w");

        if (!in_file) begin
            $display("FATA: stimulus.txt not found. Run python script first");
            $finish;
        end

        // process every command in stimulus file
        while (!$feof(in_file)) begin
            @(negedge clk); // apply inputs on falling edge

            // format: [rst] [wr] [rd] [hex_data]
            status = $fscanf(in_file, "%b %b %b %h\n", rst, wr_en, rd_en, data_in);

            if (status == 4) begin
                @(posedge clk); // fifo samples
                #1; // small delay

                // successful read data, log it for python golden model
                if (rd_en && !empty) begin
                    $fdisplay(out_file, "%h", data_out);
                end
            end
        end

        $fclose(in_file);
        $fclose(out_file);
        $display("Simulation done. response.txt generated");
        $finish;
    end
endmodule