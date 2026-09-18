// (c) Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// (c) Copyright 2022-2026 Advanced Micro Devices, Inc. All rights reserved.
// 
// This file contains confidential and proprietary information
// of AMD and is protected under U.S. and international copyright
// and other intellectual property laws.
// 
// DISCLAIMER
// This disclaimer is not a license and does not grant any
// rights to the materials distributed herewith. Except as
// otherwise provided in a valid license issued to you by
// AMD, and to the maximum extent permitted by applicable
// law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
// WITH ALL FAULTS, AND AMD HEREBY DISCLAIMS ALL WARRANTIES
// AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
// BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
// INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
// (2) AMD shall not be liable (whether in contract or tort,
// including negligence, or under any other theory of
// liability) for any loss or damage of any kind or nature
// related to, arising under or in connection with these
// materials, including for any direct, or any indirect,
// special, incidental, or consequential loss or damage
// (including loss of data, profits, goodwill, or any type of
// loss or damage suffered as a result of any action brought
// by a third party) even if such damage or loss was
// reasonably foreseeable or AMD had been advised of the
// possibility of the same.
// 
// CRITICAL APPLICATIONS
// AMD products are not designed or intended to be fail-
// safe, or for use in any application requiring fail-safe
// performance, such as life-support or safety devices or
// systems, Class III medical devices, nuclear facilities,
// applications related to the deployment of airbags, or any
// other applications that could lead to death, personal
// injury, or severe property or environmental damage
// (individually and collectively, "Critical
// Applications"). Customer assumes the sole risk and
// liability of any use of AMD products in Critical
// Applications, subject only to applicable laws and
// regulations governing limitations on product liability.
// 
// THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
// PART OF THIS FILE AT ALL TIMES.
// 
// DO NOT MODIFY THIS FILE.


// IP VLNV: xilinx.com:hls:cnn_forward:1.0
// IP Revision: 2114781237

`timescale 1ns/1ps

(* IP_DEFINITION_SOURCE = "HLS" *)
(* DowngradeIPIdentifiedWarnings = "yes" *)
module solar_flare_cnn_forward_0_0 (
  s_axi_CTRL_ARADDR,
  s_axi_CTRL_ARREADY,
  s_axi_CTRL_ARVALID,
  s_axi_CTRL_AWADDR,
  s_axi_CTRL_AWREADY,
  s_axi_CTRL_AWVALID,
  s_axi_CTRL_BREADY,
  s_axi_CTRL_BRESP,
  s_axi_CTRL_BVALID,
  s_axi_CTRL_RDATA,
  s_axi_CTRL_RREADY,
  s_axi_CTRL_RRESP,
  s_axi_CTRL_RVALID,
  s_axi_CTRL_WDATA,
  s_axi_CTRL_WREADY,
  s_axi_CTRL_WSTRB,
  s_axi_CTRL_WVALID,
  ap_clk,
  ap_rst_n,
  interrupt,
  m_axi_DATA_IN_ARADDR,
  m_axi_DATA_IN_ARBURST,
  m_axi_DATA_IN_ARCACHE,
  m_axi_DATA_IN_ARID,
  m_axi_DATA_IN_ARLEN,
  m_axi_DATA_IN_ARLOCK,
  m_axi_DATA_IN_ARPROT,
  m_axi_DATA_IN_ARQOS,
  m_axi_DATA_IN_ARREADY,
  m_axi_DATA_IN_ARREGION,
  m_axi_DATA_IN_ARSIZE,
  m_axi_DATA_IN_ARVALID,
  m_axi_DATA_IN_AWADDR,
  m_axi_DATA_IN_AWBURST,
  m_axi_DATA_IN_AWCACHE,
  m_axi_DATA_IN_AWID,
  m_axi_DATA_IN_AWLEN,
  m_axi_DATA_IN_AWLOCK,
  m_axi_DATA_IN_AWPROT,
  m_axi_DATA_IN_AWQOS,
  m_axi_DATA_IN_AWREADY,
  m_axi_DATA_IN_AWREGION,
  m_axi_DATA_IN_AWSIZE,
  m_axi_DATA_IN_AWVALID,
  m_axi_DATA_IN_BID,
  m_axi_DATA_IN_BREADY,
  m_axi_DATA_IN_BRESP,
  m_axi_DATA_IN_BVALID,
  m_axi_DATA_IN_RDATA,
  m_axi_DATA_IN_RID,
  m_axi_DATA_IN_RLAST,
  m_axi_DATA_IN_RREADY,
  m_axi_DATA_IN_RRESP,
  m_axi_DATA_IN_RVALID,
  m_axi_DATA_IN_WDATA,
  m_axi_DATA_IN_WID,
  m_axi_DATA_IN_WLAST,
  m_axi_DATA_IN_WREADY,
  m_axi_DATA_IN_WSTRB,
  m_axi_DATA_IN_WVALID
);

(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARADDR" *)
(* X_INTERFACE_MODE = "slave" *)
(* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME s_axi_CTRL, ADDR_WIDTH 6, DATA_WIDTH 32, PROTOCOL AXI4LITE, READ_WRITE_MODE READ_WRITE, FREQ_HZ 100000000, ID_WIDTH 0, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, HAS_BURST 0, HAS_LOCK 0, HAS_PROT 0, HAS_CACHE 0, HAS_QOS 0, HAS_REGION 0, HAS_WSTRB 1, HAS_BRESP 1, HAS_RRESP 1, SUPPORTS_NARROW_BURST 0, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1, MAX_BURST_LENGTH 1, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, NUM_READ_T\
HREADS 1, NUM_WRITE_THREADS 1, RUSER_BITS_PER_BYTE 0, WUSER_BITS_PER_BYTE 0, INSERT_VIP 0" *)
input wire [5 : 0] s_axi_CTRL_ARADDR;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARREADY" *)
output wire s_axi_CTRL_ARREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARVALID" *)
input wire s_axi_CTRL_ARVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWADDR" *)
input wire [5 : 0] s_axi_CTRL_AWADDR;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWREADY" *)
output wire s_axi_CTRL_AWREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWVALID" *)
input wire s_axi_CTRL_AWVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL BREADY" *)
input wire s_axi_CTRL_BREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL BRESP" *)
output wire [1 : 0] s_axi_CTRL_BRESP;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL BVALID" *)
output wire s_axi_CTRL_BVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RDATA" *)
output wire [31 : 0] s_axi_CTRL_RDATA;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RREADY" *)
input wire s_axi_CTRL_RREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RRESP" *)
output wire [1 : 0] s_axi_CTRL_RRESP;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RVALID" *)
output wire s_axi_CTRL_RVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WDATA" *)
input wire [31 : 0] s_axi_CTRL_WDATA;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WREADY" *)
output wire s_axi_CTRL_WREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WSTRB" *)
input wire [3 : 0] s_axi_CTRL_WSTRB;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WVALID" *)
input wire s_axi_CTRL_WVALID;
(* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 ap_clk CLK" *)
(* X_INTERFACE_MODE = "slave" *)
(* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME ap_clk, ASSOCIATED_BUSIF s_axi_CTRL:m_axi_DATA_IN, ASSOCIATED_RESET ap_rst_n, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, INSERT_VIP 0" *)
input wire ap_clk;
(* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 ap_rst_n RST" *)
(* X_INTERFACE_MODE = "slave" *)
(* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME ap_rst_n, POLARITY ACTIVE_LOW, INSERT_VIP 0" *)
input wire ap_rst_n;
(* X_INTERFACE_INFO = "xilinx.com:signal:interrupt:1.0 interrupt INTERRUPT" *)
(* X_INTERFACE_MODE = "master" *)
(* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME interrupt, SENSITIVITY LEVEL_HIGH, PortWidth 1" *)
output wire interrupt;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARADDR" *)
(* X_INTERFACE_MODE = "master" *)
(* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME m_axi_DATA_IN, NUM_READ_OUTSTANDING 16, NUM_WRITE_OUTSTANDING 16, MAX_READ_BURST_LENGTH 16, MAX_WRITE_BURST_LENGTH 16, MAX_BURST_LENGTH 256, PROTOCOL AXI4, READ_WRITE_MODE READ_ONLY, HAS_BURST 0, SUPPORTS_NARROW_BURST 0, ADDR_WIDTH 64, DATA_WIDTH 32, FREQ_HZ 100000000, ID_WIDTH 1, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, HAS_LOCK 1, HAS_PROT 1, HAS_CACHE 1, HAS_QOS 1, HAS_REGION 1, HAS_WSTRB 1, HAS_BRESP 1, HAS_RRESP 1, PHASE 0.0, CLK_DOMAIN \
solar_flare_processing_system7_0_0_FCLK_CLK0, NUM_READ_THREADS 1, NUM_WRITE_THREADS 1, RUSER_BITS_PER_BYTE 0, WUSER_BITS_PER_BYTE 0, INSERT_VIP 0" *)
output wire [63 : 0] m_axi_DATA_IN_ARADDR;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARBURST" *)
output wire [1 : 0] m_axi_DATA_IN_ARBURST;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARCACHE" *)
output wire [3 : 0] m_axi_DATA_IN_ARCACHE;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARID" *)
output wire [0 : 0] m_axi_DATA_IN_ARID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARLEN" *)
output wire [7 : 0] m_axi_DATA_IN_ARLEN;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARLOCK" *)
output wire [1 : 0] m_axi_DATA_IN_ARLOCK;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARPROT" *)
output wire [2 : 0] m_axi_DATA_IN_ARPROT;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARQOS" *)
output wire [3 : 0] m_axi_DATA_IN_ARQOS;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARREADY" *)
input wire m_axi_DATA_IN_ARREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARREGION" *)
output wire [3 : 0] m_axi_DATA_IN_ARREGION;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARSIZE" *)
output wire [2 : 0] m_axi_DATA_IN_ARSIZE;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARVALID" *)
output wire m_axi_DATA_IN_ARVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWADDR" *)
output wire [63 : 0] m_axi_DATA_IN_AWADDR;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWBURST" *)
output wire [1 : 0] m_axi_DATA_IN_AWBURST;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWCACHE" *)
output wire [3 : 0] m_axi_DATA_IN_AWCACHE;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWID" *)
output wire [0 : 0] m_axi_DATA_IN_AWID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWLEN" *)
output wire [7 : 0] m_axi_DATA_IN_AWLEN;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWLOCK" *)
output wire [1 : 0] m_axi_DATA_IN_AWLOCK;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWPROT" *)
output wire [2 : 0] m_axi_DATA_IN_AWPROT;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWQOS" *)
output wire [3 : 0] m_axi_DATA_IN_AWQOS;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWREADY" *)
input wire m_axi_DATA_IN_AWREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWREGION" *)
output wire [3 : 0] m_axi_DATA_IN_AWREGION;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWSIZE" *)
output wire [2 : 0] m_axi_DATA_IN_AWSIZE;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWVALID" *)
output wire m_axi_DATA_IN_AWVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BID" *)
input wire [0 : 0] m_axi_DATA_IN_BID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BREADY" *)
output wire m_axi_DATA_IN_BREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BRESP" *)
input wire [1 : 0] m_axi_DATA_IN_BRESP;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BVALID" *)
input wire m_axi_DATA_IN_BVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RDATA" *)
input wire [31 : 0] m_axi_DATA_IN_RDATA;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RID" *)
input wire [0 : 0] m_axi_DATA_IN_RID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RLAST" *)
input wire m_axi_DATA_IN_RLAST;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RREADY" *)
output wire m_axi_DATA_IN_RREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RRESP" *)
input wire [1 : 0] m_axi_DATA_IN_RRESP;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RVALID" *)
input wire m_axi_DATA_IN_RVALID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WDATA" *)
output wire [31 : 0] m_axi_DATA_IN_WDATA;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WID" *)
output wire [0 : 0] m_axi_DATA_IN_WID;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WLAST" *)
output wire m_axi_DATA_IN_WLAST;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WREADY" *)
input wire m_axi_DATA_IN_WREADY;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WSTRB" *)
output wire [3 : 0] m_axi_DATA_IN_WSTRB;
(* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WVALID" *)
output wire m_axi_DATA_IN_WVALID;

(* SDX_KERNEL = "true" *)
(* SDX_KERNEL_TYPE = "hls" *)
(* SDX_KERNEL_SIM_INST = "" *)
  cnn_forward #(
    .C_S_AXI_CTRL_ADDR_WIDTH(6),
    .C_S_AXI_CTRL_DATA_WIDTH(32),
    .C_M_AXI_DATA_IN_ID_WIDTH(1),
    .C_M_AXI_DATA_IN_ADDR_WIDTH(64),
    .C_M_AXI_DATA_IN_DATA_WIDTH(32),
    .C_M_AXI_DATA_IN_AWUSER_WIDTH(1),
    .C_M_AXI_DATA_IN_ARUSER_WIDTH(1),
    .C_M_AXI_DATA_IN_WUSER_WIDTH(1),
    .C_M_AXI_DATA_IN_RUSER_WIDTH(1),
    .C_M_AXI_DATA_IN_BUSER_WIDTH(1),
    .C_M_AXI_DATA_IN_USER_VALUE(32'H00000000),
    .C_M_AXI_DATA_IN_PROT_VALUE(3'B000),
    .C_M_AXI_DATA_IN_CACHE_VALUE(4'B0011)
  ) inst (
    .s_axi_CTRL_ARADDR(s_axi_CTRL_ARADDR),
    .s_axi_CTRL_ARREADY(s_axi_CTRL_ARREADY),
    .s_axi_CTRL_ARVALID(s_axi_CTRL_ARVALID),
    .s_axi_CTRL_AWADDR(s_axi_CTRL_AWADDR),
    .s_axi_CTRL_AWREADY(s_axi_CTRL_AWREADY),
    .s_axi_CTRL_AWVALID(s_axi_CTRL_AWVALID),
    .s_axi_CTRL_BREADY(s_axi_CTRL_BREADY),
    .s_axi_CTRL_BRESP(s_axi_CTRL_BRESP),
    .s_axi_CTRL_BVALID(s_axi_CTRL_BVALID),
    .s_axi_CTRL_RDATA(s_axi_CTRL_RDATA),
    .s_axi_CTRL_RREADY(s_axi_CTRL_RREADY),
    .s_axi_CTRL_RRESP(s_axi_CTRL_RRESP),
    .s_axi_CTRL_RVALID(s_axi_CTRL_RVALID),
    .s_axi_CTRL_WDATA(s_axi_CTRL_WDATA),
    .s_axi_CTRL_WREADY(s_axi_CTRL_WREADY),
    .s_axi_CTRL_WSTRB(s_axi_CTRL_WSTRB),
    .s_axi_CTRL_WVALID(s_axi_CTRL_WVALID),
    .ap_clk(ap_clk),
    .ap_rst_n(ap_rst_n),
    .interrupt(interrupt),
    .m_axi_DATA_IN_ARADDR(m_axi_DATA_IN_ARADDR),
    .m_axi_DATA_IN_ARBURST(m_axi_DATA_IN_ARBURST),
    .m_axi_DATA_IN_ARCACHE(m_axi_DATA_IN_ARCACHE),
    .m_axi_DATA_IN_ARID(m_axi_DATA_IN_ARID),
    .m_axi_DATA_IN_ARLEN(m_axi_DATA_IN_ARLEN),
    .m_axi_DATA_IN_ARLOCK(m_axi_DATA_IN_ARLOCK),
    .m_axi_DATA_IN_ARPROT(m_axi_DATA_IN_ARPROT),
    .m_axi_DATA_IN_ARQOS(m_axi_DATA_IN_ARQOS),
    .m_axi_DATA_IN_ARREADY(m_axi_DATA_IN_ARREADY),
    .m_axi_DATA_IN_ARREGION(m_axi_DATA_IN_ARREGION),
    .m_axi_DATA_IN_ARSIZE(m_axi_DATA_IN_ARSIZE),
    .m_axi_DATA_IN_ARUSER(),
    .m_axi_DATA_IN_ARVALID(m_axi_DATA_IN_ARVALID),
    .m_axi_DATA_IN_AWADDR(m_axi_DATA_IN_AWADDR),
    .m_axi_DATA_IN_AWBURST(m_axi_DATA_IN_AWBURST),
    .m_axi_DATA_IN_AWCACHE(m_axi_DATA_IN_AWCACHE),
    .m_axi_DATA_IN_AWID(m_axi_DATA_IN_AWID),
    .m_axi_DATA_IN_AWLEN(m_axi_DATA_IN_AWLEN),
    .m_axi_DATA_IN_AWLOCK(m_axi_DATA_IN_AWLOCK),
    .m_axi_DATA_IN_AWPROT(m_axi_DATA_IN_AWPROT),
    .m_axi_DATA_IN_AWQOS(m_axi_DATA_IN_AWQOS),
    .m_axi_DATA_IN_AWREADY(m_axi_DATA_IN_AWREADY),
    .m_axi_DATA_IN_AWREGION(m_axi_DATA_IN_AWREGION),
    .m_axi_DATA_IN_AWSIZE(m_axi_DATA_IN_AWSIZE),
    .m_axi_DATA_IN_AWUSER(),
    .m_axi_DATA_IN_AWVALID(m_axi_DATA_IN_AWVALID),
    .m_axi_DATA_IN_BID(m_axi_DATA_IN_BID),
    .m_axi_DATA_IN_BREADY(m_axi_DATA_IN_BREADY),
    .m_axi_DATA_IN_BRESP(m_axi_DATA_IN_BRESP),
    .m_axi_DATA_IN_BUSER(1'B0),
    .m_axi_DATA_IN_BVALID(m_axi_DATA_IN_BVALID),
    .m_axi_DATA_IN_RDATA(m_axi_DATA_IN_RDATA),
    .m_axi_DATA_IN_RID(m_axi_DATA_IN_RID),
    .m_axi_DATA_IN_RLAST(m_axi_DATA_IN_RLAST),
    .m_axi_DATA_IN_RREADY(m_axi_DATA_IN_RREADY),
    .m_axi_DATA_IN_RRESP(m_axi_DATA_IN_RRESP),
    .m_axi_DATA_IN_RUSER(1'B0),
    .m_axi_DATA_IN_RVALID(m_axi_DATA_IN_RVALID),
    .m_axi_DATA_IN_WDATA(m_axi_DATA_IN_WDATA),
    .m_axi_DATA_IN_WID(m_axi_DATA_IN_WID),
    .m_axi_DATA_IN_WLAST(m_axi_DATA_IN_WLAST),
    .m_axi_DATA_IN_WREADY(m_axi_DATA_IN_WREADY),
    .m_axi_DATA_IN_WSTRB(m_axi_DATA_IN_WSTRB),
    .m_axi_DATA_IN_WUSER(),
    .m_axi_DATA_IN_WVALID(m_axi_DATA_IN_WVALID)
  );
endmodule
