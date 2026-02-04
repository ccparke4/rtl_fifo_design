`timescale 1ns/1ps

module async_fifo #(
    parameter int DATA_WIDTH = 8,
    parameter int ADDR_WIDTH = 5
) (
    // write domain - source
    input   logic                   wclk,       // Fast clock
    input   logic                   wrst_n,     // async reset
    input   logic                   winc,       // write enable
    input   logic [DATA_WIDTH-1:0]  wdata,      // data to write
    output  logic                   wfull,      // stop writing flag

    // read domain - destination
    input   logic                   rclk,       // slow clock
    input   logic                   rrst_n,     // async reset
    input   logic                   rinc,       // read enable
    output  logic [DATA_WIDTH-1:0]  rdata,      // data readout
    output  logic                   rempty      // stop reading flag
);

    // signal declerations ----------------------------------------------------

    // depth is 2^ADDR_WIDTH
    localparam int DEPTH = 1 << ADDR_WIDTH;

    // Physical memory array
    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    // 2 pointers
    // binary (wbin, rbin) -> used to calculated next address
    // gray   (wptr, rbin) -> used to communicate with the other clock domain
    logic [ADDR_WIDTH:0] wptr, wbin, wgray_next, wbin_next;
    logic [ADDR_WIDTH:0] rptr, rbin, rgray_next, rbin_next;

    // 'crossed' pointers
    logic [ADDR_WIDTH:0] wq2_rptr;  // read ptr seen in write domain
    logic [ADDR_WIDTH:0] rq2_wptr;  // wrte ptr seen in read domain

    // Memory addresses derived from binary ptrs
    // Drop extra MSB for the actual memory address
    // example ptr = 10000 (16), addr = 0000 (0) -> handles wrap around
    logic [ADDR_WIDTH-1:0] waddr, raddr;

    assign waddr = wbin[ADDR_WIDTH-1:0];
    assign raddr = rbin[ADDR_WIDTH-1:0];

    // Memory access (dual port RAM) -------------------------------------------
    // std. ram interface. Writ happens on WCLK, read is combinational 
    always_ff @(posedge wclk) begin
        if (winc && !wfull)
            mem[waddr] <= wdata;
    end

    assign rdata = mem[raddr];

    // syncronizers ------------------------------------------------------------
    // 2 FF synchronizer to move ptr
    // signal arrives while clk rising q1 might be between 0/1,
    // q2 waits one cycle for stability
    
    // move read ptr -> into write domain
    logic [ADDR_WIDTH:0] wq1_rptr;
    always_ff @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) {wq2_rptr, wq1_rptr} <= '0;
        else         {wq2_rptr, wq1_rptr} <= {wq1_rptr, rptr};
    end 

    // move write pointer -> into read domain
    logic [ADDR_WIDTH:0] rq1_wptr;
    always_ff @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) {rq2_wptr, rq1_wptr} <= '0;
        else         {rq2_wptr, rq1_wptr} <= {rq1_wptr, wptr};
    end

    // write domain logic ------------------------------------------------------
    
    // Calculate next pointers
    // Binary: add 1
    // gray:   << 1 then Xor w/ binary
    // Ex
    //      binary 3 (0011) -> shift (0001) -> XOR = 0010 (gray 3)
    //      binary 4 (0100) -> shift (0010) -> XOR = 0110 (gray 4)

    assign wbin_next  = wbin + (winc & ~wfull);
    assign wgray_next = (wbin_next >> 1) ^ wbin_next;

    always_ff@(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) begin
            wbin <= '0;
            wptr <= '0;
        end else begin
            wbin <= wbin_next;
            wptr <= wgray_next;
        end
    end 

    // generate FULL flag
    // FIFO is full when the write pointer catches the read pointer from behind
    // in binary means idx's match, but MSB (lay bit) is different
    // in gray code patter is different
    //  MSB must be diff
    //  2nd MSB must be diff
    //  all other bits match
    
    // check against the sync'd read ptr q2
    logic wfull_val;
    assign wfull_val = (wgray_next == {~wq2_rptr[ADDR_WIDTH:ADDR_WIDTH-1],
                                        wq2_rptr[ADDR_WIDTH-2:0]});

    always_ff @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) wfull <= 1'b0;
        else         wfull <= wfull_val;
    end

    // read domain logic -------------------------------------------------------

    // calculate next pointers
    assign rbin_next  = rbin + (rinc & ~rempty);
    assign rgray_next = (rbin_next >> 1) ^ rbin_next;

    always_ff @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) begin
            rbin <= '0;
            rptr <= '0;
        end else begin
            rbin <= rbin_next;
            rptr <= rgray_next;
        end
    end

    // generate EMPTY flag
    // empty is when the ptrs are identical
    // compare the next read gray ptr w/ sync'd write gray ptr
    
    logic rempty_val;
    assign rempty_val = (rgray_next == rq2_wptr);

    always_ff @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) rempty <= 1'b1;    // default to empty on reset
        else         rempty <= rempty_val;
    end

endmodule