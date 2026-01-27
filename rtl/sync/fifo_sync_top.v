`timescale 1ns / 1ps

module fifo_sync_top
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
    reg overflow_reg;
    reg underflow_reg;
    assign overflow = overflow_reg;  
    assign underflow = underflow_reg;
    
    always @(posedge clk or posedge rst) begin
    if (rst) begin
        overflow_reg  <= 1'b0;
        underflow_reg <= 1'b0;
    end else begin
        // Stick High if we try to write when full
        if (full && wr_en)
            overflow_reg <= 1'b1;
            
        // Stick High if we try to read when empty
        if (empty && rd_en)
            underflow_reg <= 1'b1;
    end
end
    
    // Instantiate module -----------------------------
    fifo_sync #(
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
    