`timescale 1ns / 1ps

module fifo_sync_top #(
    parameter int DATA_WIDTH = 8,
    parameter int ADDR_WIDTH = 5
)(
    input  logic clk,
    input  logic rst_n,
    input  logic wr_en,
    input  logic rd_en,
    input  logic [DATA_WIDTH-1:0] data_in,
    output logic [DATA_WIDTH-1:0] data_out,
    output logic full,
    output logic empty
);
    
    localparam int DEPTH = 1 << ADDR_WIDTH;

    // Internal Mem and pointers
    logic [DATA_WIDTH-1:0] mem [DEPTH];
    logic [ADDR_WIDTH-1:0] wr_ptr, rd_ptr;
    logic [ADDR_WIDTH:0]   count;           // using extra bit as full/empty detection

    // status flags
    assign empty = (count == 0);
    assign full  = (count == DEPTH);

    // FWFT: cominational read output
    assign data_out = mem[rd_ptr];

    // sequential logic: pointer and mem
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr    <= '0;
            rd_ptr    <= '0;
            count     <= 1'b0;
        end else begin
            // Write Logic
            if (wr_en && !full) begin
                mem[wr_ptr] <= data_in;
                wr_ptr      <= wr_ptr + 1'b1;
            end 

            // read logic
            if (rd_en && !empty) begin
                rd_ptr   <= rd_ptr + 1'b1;
            end

            // counter logic
            case ({ (wr_en && !full), (rd_en && !empty) }) 
                2'b10: count <= count + 1'b1;   // write only
                2'b01: count <= count - 1'b1;   // read only
                default: count <= count;
            endcase
        end
    end
    
 endmodule
    