// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2026.1 (lin64) Build 6511674 Tue Jun 16 11:01:26 MDT 2026
// Date        : Fri Sep 11 15:58:49 2026
// Host        : Nitro-ANV15-42 running 64-bit Ubuntu 24.04.4 LTS
// Command     : write_verilog -force -mode synth_stub
//               /home/jyothish/solar-flare-swan-fpga/vivado/solar_flare/solar_flare.gen/sources_1/bd/solar_flare/ip/solar_flare_cnn_forward_0_0/solar_flare_cnn_forward_0_0_stub.v
// Design      : solar_flare_cnn_forward_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7z010clg400-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "solar_flare_cnn_forward_0_0,cnn_forward,{}" *) (* CORE_GENERATION_INFO = "solar_flare_cnn_forward_0_0,cnn_forward,{x_ipProduct=Vivado 2026.1,x_ipVendor=xilinx.com,x_ipLibrary=hls,x_ipName=cnn_forward,x_ipVersion=1.0,x_ipCoreRevision=2114781237,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,C_S_AXI_CTRL_ADDR_WIDTH=6,C_S_AXI_CTRL_DATA_WIDTH=32,C_M_AXI_DATA_IN_ID_WIDTH=1,C_M_AXI_DATA_IN_ADDR_WIDTH=64,C_M_AXI_DATA_IN_DATA_WIDTH=32,C_M_AXI_DATA_IN_AWUSER_WIDTH=1,C_M_AXI_DATA_IN_ARUSER_WIDTH=1,C_M_AXI_DATA_IN_WUSER_WIDTH=1,C_M_AXI_DATA_IN_RUSER_WIDTH=1,C_M_AXI_DATA_IN_BUSER_WIDTH=1,C_M_AXI_DATA_IN_USER_VALUE=0x00000000,C_M_AXI_DATA_IN_PROT_VALUE=000,C_M_AXI_DATA_IN_CACHE_VALUE=0011}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* IP_DEFINITION_SOURCE = "HLS" *) (* X_CORE_INFO = "cnn_forward,Vivado 2026.1" *) (* hls_module = "yes" *) 
module solar_flare_cnn_forward_0_0(s_axi_CTRL_ARADDR, s_axi_CTRL_ARREADY, 
  s_axi_CTRL_ARVALID, s_axi_CTRL_AWADDR, s_axi_CTRL_AWREADY, s_axi_CTRL_AWVALID, 
  s_axi_CTRL_BREADY, s_axi_CTRL_BRESP, s_axi_CTRL_BVALID, s_axi_CTRL_RDATA, 
  s_axi_CTRL_RREADY, s_axi_CTRL_RRESP, s_axi_CTRL_RVALID, s_axi_CTRL_WDATA, 
  s_axi_CTRL_WREADY, s_axi_CTRL_WSTRB, s_axi_CTRL_WVALID, ap_clk, ap_rst_n, interrupt, 
  m_axi_DATA_IN_ARADDR, m_axi_DATA_IN_ARBURST, m_axi_DATA_IN_ARCACHE, m_axi_DATA_IN_ARID, 
  m_axi_DATA_IN_ARLEN, m_axi_DATA_IN_ARLOCK, m_axi_DATA_IN_ARPROT, m_axi_DATA_IN_ARQOS, 
  m_axi_DATA_IN_ARREADY, m_axi_DATA_IN_ARREGION, m_axi_DATA_IN_ARSIZE, 
  m_axi_DATA_IN_ARVALID, m_axi_DATA_IN_AWADDR, m_axi_DATA_IN_AWBURST, 
  m_axi_DATA_IN_AWCACHE, m_axi_DATA_IN_AWID, m_axi_DATA_IN_AWLEN, m_axi_DATA_IN_AWLOCK, 
  m_axi_DATA_IN_AWPROT, m_axi_DATA_IN_AWQOS, m_axi_DATA_IN_AWREADY, 
  m_axi_DATA_IN_AWREGION, m_axi_DATA_IN_AWSIZE, m_axi_DATA_IN_AWVALID, m_axi_DATA_IN_BID, 
  m_axi_DATA_IN_BREADY, m_axi_DATA_IN_BRESP, m_axi_DATA_IN_BVALID, m_axi_DATA_IN_RDATA, 
  m_axi_DATA_IN_RID, m_axi_DATA_IN_RLAST, m_axi_DATA_IN_RREADY, m_axi_DATA_IN_RRESP, 
  m_axi_DATA_IN_RVALID, m_axi_DATA_IN_WDATA, m_axi_DATA_IN_WID, m_axi_DATA_IN_WLAST, 
  m_axi_DATA_IN_WREADY, m_axi_DATA_IN_WSTRB, m_axi_DATA_IN_WVALID)
/* synthesis syn_black_box black_box_pad_pin="s_axi_CTRL_ARADDR[5:0],s_axi_CTRL_ARREADY,s_axi_CTRL_ARVALID,s_axi_CTRL_AWADDR[5:0],s_axi_CTRL_AWREADY,s_axi_CTRL_AWVALID,s_axi_CTRL_BREADY,s_axi_CTRL_BRESP[1:0],s_axi_CTRL_BVALID,s_axi_CTRL_RDATA[31:0],s_axi_CTRL_RREADY,s_axi_CTRL_RRESP[1:0],s_axi_CTRL_RVALID,s_axi_CTRL_WDATA[31:0],s_axi_CTRL_WREADY,s_axi_CTRL_WSTRB[3:0],s_axi_CTRL_WVALID,ap_rst_n,interrupt,m_axi_DATA_IN_ARADDR[63:0],m_axi_DATA_IN_ARBURST[1:0],m_axi_DATA_IN_ARCACHE[3:0],m_axi_DATA_IN_ARID[0:0],m_axi_DATA_IN_ARLEN[7:0],m_axi_DATA_IN_ARLOCK[1:0],m_axi_DATA_IN_ARPROT[2:0],m_axi_DATA_IN_ARQOS[3:0],m_axi_DATA_IN_ARREADY,m_axi_DATA_IN_ARREGION[3:0],m_axi_DATA_IN_ARSIZE[2:0],m_axi_DATA_IN_ARVALID,m_axi_DATA_IN_AWADDR[63:0],m_axi_DATA_IN_AWBURST[1:0],m_axi_DATA_IN_AWCACHE[3:0],m_axi_DATA_IN_AWID[0:0],m_axi_DATA_IN_AWLEN[7:0],m_axi_DATA_IN_AWLOCK[1:0],m_axi_DATA_IN_AWPROT[2:0],m_axi_DATA_IN_AWQOS[3:0],m_axi_DATA_IN_AWREADY,m_axi_DATA_IN_AWREGION[3:0],m_axi_DATA_IN_AWSIZE[2:0],m_axi_DATA_IN_AWVALID,m_axi_DATA_IN_BID[0:0],m_axi_DATA_IN_BREADY,m_axi_DATA_IN_BRESP[1:0],m_axi_DATA_IN_BVALID,m_axi_DATA_IN_RDATA[31:0],m_axi_DATA_IN_RID[0:0],m_axi_DATA_IN_RLAST,m_axi_DATA_IN_RREADY,m_axi_DATA_IN_RRESP[1:0],m_axi_DATA_IN_RVALID,m_axi_DATA_IN_WDATA[31:0],m_axi_DATA_IN_WID[0:0],m_axi_DATA_IN_WLAST,m_axi_DATA_IN_WREADY,m_axi_DATA_IN_WSTRB[3:0],m_axi_DATA_IN_WVALID" */
/* synthesis syn_force_seq_prim="ap_clk" */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARADDR" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME s_axi_CTRL, ADDR_WIDTH 6, DATA_WIDTH 32, PROTOCOL AXI4LITE, READ_WRITE_MODE READ_WRITE, FREQ_HZ 100000000, ID_WIDTH 0, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, HAS_BURST 0, HAS_LOCK 0, HAS_PROT 0, HAS_CACHE 0, HAS_QOS 0, HAS_REGION 0, HAS_WSTRB 1, HAS_BRESP 1, HAS_RRESP 1, SUPPORTS_NARROW_BURST 0, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1, MAX_BURST_LENGTH 1, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, NUM_READ_THREADS 1, NUM_WRITE_THREADS 1, RUSER_BITS_PER_BYTE 0, WUSER_BITS_PER_BYTE 0, INSERT_VIP 0" *) input [5:0]s_axi_CTRL_ARADDR;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARREADY" *) output s_axi_CTRL_ARREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARVALID" *) input s_axi_CTRL_ARVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWADDR" *) input [5:0]s_axi_CTRL_AWADDR;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWREADY" *) output s_axi_CTRL_AWREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWVALID" *) input s_axi_CTRL_AWVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL BREADY" *) input s_axi_CTRL_BREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL BRESP" *) output [1:0]s_axi_CTRL_BRESP;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL BVALID" *) output s_axi_CTRL_BVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RDATA" *) output [31:0]s_axi_CTRL_RDATA;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RREADY" *) input s_axi_CTRL_RREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RRESP" *) output [1:0]s_axi_CTRL_RRESP;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL RVALID" *) output s_axi_CTRL_RVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WDATA" *) input [31:0]s_axi_CTRL_WDATA;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WREADY" *) output s_axi_CTRL_WREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WSTRB" *) input [3:0]s_axi_CTRL_WSTRB;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi_CTRL WVALID" *) input s_axi_CTRL_WVALID;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 ap_clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME ap_clk, ASSOCIATED_BUSIF s_axi_CTRL:m_axi_DATA_IN, ASSOCIATED_RESET ap_rst_n, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, INSERT_VIP 0" *) input ap_clk /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 ap_rst_n RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME ap_rst_n, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input ap_rst_n;
  (* X_INTERFACE_INFO = "xilinx.com:signal:interrupt:1.0 interrupt INTERRUPT" *) (* X_INTERFACE_MODE = "master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME interrupt, SENSITIVITY LEVEL_HIGH, PortWidth 1" *) output interrupt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARADDR" *) (* X_INTERFACE_MODE = "master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME m_axi_DATA_IN, NUM_READ_OUTSTANDING 16, NUM_WRITE_OUTSTANDING 16, MAX_READ_BURST_LENGTH 16, MAX_WRITE_BURST_LENGTH 16, MAX_BURST_LENGTH 256, PROTOCOL AXI4, READ_WRITE_MODE READ_ONLY, HAS_BURST 0, SUPPORTS_NARROW_BURST 0, ADDR_WIDTH 64, DATA_WIDTH 32, FREQ_HZ 100000000, ID_WIDTH 1, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, HAS_LOCK 1, HAS_PROT 1, HAS_CACHE 1, HAS_QOS 1, HAS_REGION 1, HAS_WSTRB 1, HAS_BRESP 1, HAS_RRESP 1, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, NUM_READ_THREADS 1, NUM_WRITE_THREADS 1, RUSER_BITS_PER_BYTE 0, WUSER_BITS_PER_BYTE 0, INSERT_VIP 0" *) output [63:0]m_axi_DATA_IN_ARADDR;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARBURST" *) output [1:0]m_axi_DATA_IN_ARBURST;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARCACHE" *) output [3:0]m_axi_DATA_IN_ARCACHE;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARID" *) output [0:0]m_axi_DATA_IN_ARID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARLEN" *) output [7:0]m_axi_DATA_IN_ARLEN;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARLOCK" *) output [1:0]m_axi_DATA_IN_ARLOCK;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARPROT" *) output [2:0]m_axi_DATA_IN_ARPROT;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARQOS" *) output [3:0]m_axi_DATA_IN_ARQOS;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARREADY" *) input m_axi_DATA_IN_ARREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARREGION" *) output [3:0]m_axi_DATA_IN_ARREGION;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARSIZE" *) output [2:0]m_axi_DATA_IN_ARSIZE;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARVALID" *) output m_axi_DATA_IN_ARVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWADDR" *) output [63:0]m_axi_DATA_IN_AWADDR;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWBURST" *) output [1:0]m_axi_DATA_IN_AWBURST;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWCACHE" *) output [3:0]m_axi_DATA_IN_AWCACHE;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWID" *) output [0:0]m_axi_DATA_IN_AWID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWLEN" *) output [7:0]m_axi_DATA_IN_AWLEN;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWLOCK" *) output [1:0]m_axi_DATA_IN_AWLOCK;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWPROT" *) output [2:0]m_axi_DATA_IN_AWPROT;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWQOS" *) output [3:0]m_axi_DATA_IN_AWQOS;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWREADY" *) input m_axi_DATA_IN_AWREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWREGION" *) output [3:0]m_axi_DATA_IN_AWREGION;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWSIZE" *) output [2:0]m_axi_DATA_IN_AWSIZE;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWVALID" *) output m_axi_DATA_IN_AWVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BID" *) input [0:0]m_axi_DATA_IN_BID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BREADY" *) output m_axi_DATA_IN_BREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BRESP" *) input [1:0]m_axi_DATA_IN_BRESP;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BVALID" *) input m_axi_DATA_IN_BVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RDATA" *) input [31:0]m_axi_DATA_IN_RDATA;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RID" *) input [0:0]m_axi_DATA_IN_RID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RLAST" *) input m_axi_DATA_IN_RLAST;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RREADY" *) output m_axi_DATA_IN_RREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RRESP" *) input [1:0]m_axi_DATA_IN_RRESP;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RVALID" *) input m_axi_DATA_IN_RVALID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WDATA" *) output [31:0]m_axi_DATA_IN_WDATA;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WID" *) output [0:0]m_axi_DATA_IN_WID;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WLAST" *) output m_axi_DATA_IN_WLAST;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WREADY" *) input m_axi_DATA_IN_WREADY;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WSTRB" *) output [3:0]m_axi_DATA_IN_WSTRB;
  (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WVALID" *) output m_axi_DATA_IN_WVALID;
endmodule
