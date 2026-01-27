`timescale 1ns / 1ps

module fifo_sync
    #(
        // param declerations
        parameter AWIDTH = 5,   // address width
        parameter DWIDTH = 8    // depth width
    )(
        // port declarations
        input clk, rst, wr_en, rd_en,
        input [DWIDTH-1:0] data_in,
        output full, empty,
        output reg [DWIDTH-1:0] data_out
    );
    
    localparam depth = 2**AWIDTH;
    reg [DWIDTH-1:0]    mem [0:depth-1];    // memory array
    
    // ptrs and flag
    reg [AWIDTH-1:0]    wptr;
    reg [AWIDTH-1:0]    rptr;
    reg wrote;
    
    // Full / Empty logic ----------------------------------------------
    assign empty = (wptr == rptr) && !wrote;
    assign full = (wptr == rptr) && wrote;
    
    // behavioral code
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            // reset pointers and write signal
            rptr     <= {AWIDTH{1'b0}};
            wptr     <= {AWIDTH{1'b0}};
            wrote    <= 1'b0;
            data_out <= {DWIDTH{1'b0}};
        end
        else begin
            // WRITE op
            if (wr_en && !full) begin
                mem[wptr] <= data_in;
                wptr      <= wptr + 1;  
                wrote     <= 1'b1;      // new data flag
            end
            
            // READ op
            if (rd_en && !empty) begin
                data_out <= mem[rptr];
                rptr     <= rptr + 1;
                wrote    <= 1'b0;       // removed data
            end
        end
    end
    
endmodule
