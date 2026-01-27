`timescale 1ns / 1ps

module tb_fifo_sync;

    // params & signals -------------------------
    parameter DATA_WIDTH = 8;
    parameter ADDR_WIDTH = 5;   // 2^5 depth
    
    // inputs to dut
    reg                     clk;
    reg                     rst;
    reg                     wr_en;
    reg                     rd_en;
    reg [DATA_WIDTH-1:0]    data_in;
    
    // outputs from DUT (wires for monitoring)
    wire [DATA_WIDTH-1:0]   data_out;
    wire                    full;
    wire                    empty;
    wire                    overflow;
    wire                    underflow;
    
    // Instantiate DUT -----------------------------
    fifo_sync_top #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) uut (
        .clk        (clk),
        .rst        (rst),
        .wr_en      (wr_en),
        .rd_en      (rd_en),
        .data_in    (data_in),
        .data_out   (data_out),
        .full       (full),
        .empty      (empty),
        .overflow   (overflow),
        .underflow  (underflow)
    );
    
    // clock gen --------------------------------------
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    // Test tasks -------------------------------------
    task write_data(input [DATA_WIDTH-1:0] val);
        begin
            @(posedge clk);     // wait for clock
            data_in = val;
            wr_en = 1;
            @(posedge clk);     // 1 cycle hold
            wr_en = 0;
        end
    endtask
    
    // task to read data
    task read_data();
        begin
            @(posedge clk);
            rd_en = 1;
            @(posedge clk);
            rd_en = 0;
        end
    endtask
    
    // test seq -------------------------------------------
    // init inputs
    integer i;
    initial begin       
        rst = 0;
        wr_en = 0;
        rd_en = 0;
        data_in = 0;
        
        // apply reset - for a bit    
        #10;
        rst = 1;
        #20
        
        rst = 0;
        
        $display("--- Reset Done ---");
        #10;
        
        // TC 1: fill FIFO
        $display("--- T1: Writing data 0x10 to 0x2F ---");
        for (i = 0; i < 32; i = i + 1) begin
            write_data(i); 
        end
        
        // full check
        #10;
        if (full) $display("SUCCESS: FIFO FULL");
        else      $display("ERROR: FIFO should be FULL");
        
        // TC 2: Try to table
        $display("--- T2: Att. Overfill ---");
        write_data(8'hFF);
        #10;
        if (overflow) $display("SUCCESS: Overflow flag detected");
        else          $display("ERROR: Overflow not detected");
        
        // TC 3: empty fifo
        $display("--- T3: Empty Fifo ---");
        repeat(32) begin
            read_data();
        end
        
        // check if empty
        #10;
        if (empty) $display("SUCCESS: FIFO is Empty");
        else       $display("ERROR: FIFO should be Empty but is not");
        
        // TC 4: Underflow
        $display("--- T4: Att. Underflow ---");
        read_data();
        #10;
        if (underflow) $display("SUCCESS: Underflow flag detected");
        else           $display("ERROR: Underflow flag missing");
        
        $display("--- Simulation Complete ---");
        $stop;
        
    end
endmodule
    
    
    
    