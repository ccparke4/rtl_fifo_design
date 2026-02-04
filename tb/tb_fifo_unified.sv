`timescale 1ns/1ps
module tb_fifo_unified;
    parameter DATA_WIDTH = 8;
    parameter ADDR_WIDTH = 5;
    
    logic wclk, rclk;
    logic rst_n;       
    logic winc, rinc;
    logic [DATA_WIDTH-1:0] wdata;
    logic wfull, rempty;
    logic [DATA_WIDTH-1:0] rdata;

    `ifdef ASYNC_MODE
        initial $display("--- TESTING ASYNC FIFO ---");
        initial wclk = 0; always #5    wclk = ~wclk;
        initial rclk = 0; always #12.5 rclk = ~rclk;
        
        async_fifo #(
            .DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH)
        ) dut (
            .wclk(wclk), .wrst_n(rst_n), .winc(winc), .wdata(wdata), .wfull(wfull),
            .rclk(rclk), .rrst_n(rst_n), .rinc(rinc), .rdata(rdata), .rempty(rempty)
        );
    `else
        initial $display("--- TESTING SYNC FIFO ---");
        initial wclk = 0; always #5 wclk = ~wclk; 
        assign rclk = wclk; 
        
        fifo_sync_top #(
            .DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH)
        ) dut (
            .clk(wclk), .rst_n(rst_n),
            .wr_en(winc), .rd_en(rinc),
            .data_in(wdata), .full(wfull), .empty(rempty), .data_out(rdata)
        );
    `endif

    integer f_in, f_out, scan_res;
    logic f_rst, f_wr, f_rd;
    logic [7:0] f_data_val;
    
    initial begin
        f_in  = $fopen("stimulus.txt", "r");
        f_out = $fopen("response.txt", "w");
        
        if (f_in == 0) begin
            $display("Error: Could not open stimulus.txt");
            $finish;
        end

        rst_n = 0; winc = 0; rinc = 0; wdata = 0;
        #100;
        rst_n = 1;
        
        `ifdef ASYNC_MODE
            // Extra settling time for synchronizers after reset
            repeat(4) @(posedge rclk);
        `endif

        while (!$feof(f_in)) begin
            scan_res = $fscanf(f_in, "%b %b %b %h\n", f_rst, f_wr, f_rd, f_data_val);
            if (scan_res != 4) continue;
            
            `ifdef ASYNC_MODE
                // ASYNC: Drive writes on wclk, reads on rclk
                if (f_wr) begin
                    @(negedge wclk);
                    rst_n = f_rst ? 1'b0 : 1'b1;
                    winc  = 1;
                    wdata = f_data_val;
                    @(negedge wclk);
                    winc  = 0;
                end
                
                if (f_rd) begin
                    @(negedge rclk);
                    rinc = 1;
                    #1;  // Combinational settle
                    // Sample rdata NOW, before posedge advances pointer
                    $fwrite(f_out, "%b %b %b %b %b %b %h\n", 
                            rclk, rst_n, winc, rinc, wfull, rempty, rdata);
                    @(posedge rclk);  // Pointer advances here
                    @(negedge rclk);
                    rinc = 0;
                end
            `else
                // SYNC: Original behavior
                @(negedge wclk);
                rst_n = f_rst ? 1'b0 : 1'b1;
                winc  = f_wr;
                rinc  = f_rd;
                wdata = f_data_val;
                
                $fwrite(f_out, "%b %b %b %b %b %b %h\n", 
                        wclk, rst_n, winc, rinc, wfull, rempty, rdata);
            `endif
        end
        
        $fclose(f_in);
        $fclose(f_out);
        $finish;
    end
endmodule