`timescale 1ns / 1ps

module fifo_sync
    #(
        parameter DATA_WIDTH = 8,
        parameter ADDR_WIDTH = 5        // 2^5=32 locations deep
    )(
        input                   clk,
        input                   rst,
        
        // Write interface
        input                   wr_en,
        input [DATA_WIDTH-1:0]  data_in,
        output                  full,
        output                  overflow,   // added error flag
        
        // Read interface
        input                   rd_en,
        output [DATA_WIDTH-1:0] data_out,
        output                  empty,
        output                  underflow   // added error flag       
    );
    
    // 1.) Protect the FIFO from illegal ops
    // only allow writing if NOT full
    wire safe_wr = wr_en && !full;
    
    // only allow reading if NOT empty
    wire safe_rd = rd_en && !empty;
    
    // 2.) generate error flag
    // overflow -> write when FIFO was full
    assign overflow = wr_en && full;
    
    // underflow -> read when FIFO empty
    assign underflow = rd_en && empty;
    
    // Instantiate module -----------------------------
    fifo_mem #(
        .DWIDTH(DATA_WIDTH),
        .AWIDTH(ADDR_WIDTH)
    )u_fifo_core(
        .clk        (clk),
        .rst        (rst),
        .wr_en      (safe_wr),  // connect the 'safe' signal
        .rd_en      (safe_rd),  // connect the 'safe' signal
        .data_in    (data_in),
        .data_out   (data_out),
        .full       (full),
        .empty      (empty)
    );
    
 endmodule
    