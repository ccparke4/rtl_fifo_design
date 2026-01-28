`timescale 1ns / 1ps

module fifo_sync_top #(
    parameter int DATA_WIDTH = 8,
    parameter int ADDR_WIDTH = 5
)(
    input  logic clk,
    input  logic rst,
    input  logic wr_en,
    input  logic rd_en,
    input  logic [DATA_WIDTH-1:0] data_in,
    output logic [DATA_WIDTH-1:0] data_out,
    output logic full,
    output logic empty,
    output logic overflow,
    output logic underflow
);
    
    localparam int DEPTH = 1 << ADDR_WIDTH;

    // Internal Mem and pointers
    logic [DATA_WIDTH-1:0] mem [DEPTH];
    logic [ADDR_WIDTH-1:0] wr_ptr, rd_ptr;
    logic [ADDR_WIDTH:0]   count;           // using extra bit as full/empty detection

    // status flags
    assign empty = (count == 0);
    assign full  = (count == DEPTH);

    // sequential logic: pointer and mem
    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            wr_ptr    <= '0;
            rd_ptr    <= '0;
            count     <= 1'b0;
            overflow   <= 1'b0;
            underflow <= 1'b0;
        end else begin
            // Write Logic
            if (wr_en && !full) begin
                mem[wr_ptr] <= data_in;
                wr_ptr      <= wr_ptr + 1'b1;
            end else if (wr_en && full) begin
                overflow <= 1'b1;   // sticky, stays high
            end

            // read logic
            if (rd_en && !empty) begin
                data_out <= mem[rd_ptr];
                rd_ptr   <= rd_ptr + 1;
            end else if (rd_en && empty) begin
                underflow <= 1'b1;
            end

            // counter logic
            if (wr_en && !full && !(rd_en && !empty)) 
                count <= count + 1'b1;
            else if (rd_en && !empty && !(wr_en && !full))
                count <= count - 1'b1;
        end

    end
    
 endmodule
    