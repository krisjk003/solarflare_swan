-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2026.1 (lin64) Build 6511674 Tue Jun 16 11:01:26 MDT 2026
-- Date        : Fri Sep 11 15:58:50 2026
-- Host        : Nitro-ANV15-42 running 64-bit Ubuntu 24.04.4 LTS
-- Command     : write_vhdl -force -mode synth_stub
--               /home/jyothish/solar-flare-swan-fpga/vivado/solar_flare/solar_flare.gen/sources_1/bd/solar_flare/ip/solar_flare_cnn_forward_0_0/solar_flare_cnn_forward_0_0_stub.vhdl
-- Design      : solar_flare_cnn_forward_0_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z010clg400-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity solar_flare_cnn_forward_0_0 is
  Port ( 
    s_axi_CTRL_ARADDR : in STD_LOGIC_VECTOR ( 5 downto 0 );
    s_axi_CTRL_ARREADY : out STD_LOGIC;
    s_axi_CTRL_ARVALID : in STD_LOGIC;
    s_axi_CTRL_AWADDR : in STD_LOGIC_VECTOR ( 5 downto 0 );
    s_axi_CTRL_AWREADY : out STD_LOGIC;
    s_axi_CTRL_AWVALID : in STD_LOGIC;
    s_axi_CTRL_BREADY : in STD_LOGIC;
    s_axi_CTRL_BRESP : out STD_LOGIC_VECTOR ( 1 downto 0 );
    s_axi_CTRL_BVALID : out STD_LOGIC;
    s_axi_CTRL_RDATA : out STD_LOGIC_VECTOR ( 31 downto 0 );
    s_axi_CTRL_RREADY : in STD_LOGIC;
    s_axi_CTRL_RRESP : out STD_LOGIC_VECTOR ( 1 downto 0 );
    s_axi_CTRL_RVALID : out STD_LOGIC;
    s_axi_CTRL_WDATA : in STD_LOGIC_VECTOR ( 31 downto 0 );
    s_axi_CTRL_WREADY : out STD_LOGIC;
    s_axi_CTRL_WSTRB : in STD_LOGIC_VECTOR ( 3 downto 0 );
    s_axi_CTRL_WVALID : in STD_LOGIC;
    ap_clk : in STD_LOGIC;
    ap_rst_n : in STD_LOGIC;
    interrupt : out STD_LOGIC;
    m_axi_DATA_IN_ARADDR : out STD_LOGIC_VECTOR ( 63 downto 0 );
    m_axi_DATA_IN_ARBURST : out STD_LOGIC_VECTOR ( 1 downto 0 );
    m_axi_DATA_IN_ARCACHE : out STD_LOGIC_VECTOR ( 3 downto 0 );
    m_axi_DATA_IN_ARID : out STD_LOGIC_VECTOR ( 0 to 0 );
    m_axi_DATA_IN_ARLEN : out STD_LOGIC_VECTOR ( 7 downto 0 );
    m_axi_DATA_IN_ARLOCK : out STD_LOGIC_VECTOR ( 1 downto 0 );
    m_axi_DATA_IN_ARPROT : out STD_LOGIC_VECTOR ( 2 downto 0 );
    m_axi_DATA_IN_ARQOS : out STD_LOGIC_VECTOR ( 3 downto 0 );
    m_axi_DATA_IN_ARREADY : in STD_LOGIC;
    m_axi_DATA_IN_ARREGION : out STD_LOGIC_VECTOR ( 3 downto 0 );
    m_axi_DATA_IN_ARSIZE : out STD_LOGIC_VECTOR ( 2 downto 0 );
    m_axi_DATA_IN_ARVALID : out STD_LOGIC;
    m_axi_DATA_IN_AWADDR : out STD_LOGIC_VECTOR ( 63 downto 0 );
    m_axi_DATA_IN_AWBURST : out STD_LOGIC_VECTOR ( 1 downto 0 );
    m_axi_DATA_IN_AWCACHE : out STD_LOGIC_VECTOR ( 3 downto 0 );
    m_axi_DATA_IN_AWID : out STD_LOGIC_VECTOR ( 0 to 0 );
    m_axi_DATA_IN_AWLEN : out STD_LOGIC_VECTOR ( 7 downto 0 );
    m_axi_DATA_IN_AWLOCK : out STD_LOGIC_VECTOR ( 1 downto 0 );
    m_axi_DATA_IN_AWPROT : out STD_LOGIC_VECTOR ( 2 downto 0 );
    m_axi_DATA_IN_AWQOS : out STD_LOGIC_VECTOR ( 3 downto 0 );
    m_axi_DATA_IN_AWREADY : in STD_LOGIC;
    m_axi_DATA_IN_AWREGION : out STD_LOGIC_VECTOR ( 3 downto 0 );
    m_axi_DATA_IN_AWSIZE : out STD_LOGIC_VECTOR ( 2 downto 0 );
    m_axi_DATA_IN_AWVALID : out STD_LOGIC;
    m_axi_DATA_IN_BID : in STD_LOGIC_VECTOR ( 0 to 0 );
    m_axi_DATA_IN_BREADY : out STD_LOGIC;
    m_axi_DATA_IN_BRESP : in STD_LOGIC_VECTOR ( 1 downto 0 );
    m_axi_DATA_IN_BVALID : in STD_LOGIC;
    m_axi_DATA_IN_RDATA : in STD_LOGIC_VECTOR ( 31 downto 0 );
    m_axi_DATA_IN_RID : in STD_LOGIC_VECTOR ( 0 to 0 );
    m_axi_DATA_IN_RLAST : in STD_LOGIC;
    m_axi_DATA_IN_RREADY : out STD_LOGIC;
    m_axi_DATA_IN_RRESP : in STD_LOGIC_VECTOR ( 1 downto 0 );
    m_axi_DATA_IN_RVALID : in STD_LOGIC;
    m_axi_DATA_IN_WDATA : out STD_LOGIC_VECTOR ( 31 downto 0 );
    m_axi_DATA_IN_WID : out STD_LOGIC_VECTOR ( 0 to 0 );
    m_axi_DATA_IN_WLAST : out STD_LOGIC;
    m_axi_DATA_IN_WREADY : in STD_LOGIC;
    m_axi_DATA_IN_WSTRB : out STD_LOGIC_VECTOR ( 3 downto 0 );
    m_axi_DATA_IN_WVALID : out STD_LOGIC
  );

  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of solar_flare_cnn_forward_0_0 : entity is "solar_flare_cnn_forward_0_0,cnn_forward,{}";
  attribute CORE_GENERATION_INFO : string;
  attribute CORE_GENERATION_INFO of solar_flare_cnn_forward_0_0 : entity is "solar_flare_cnn_forward_0_0,cnn_forward,{x_ipProduct=Vivado 2026.1,x_ipVendor=xilinx.com,x_ipLibrary=hls,x_ipName=cnn_forward,x_ipVersion=1.0,x_ipCoreRevision=2114781237,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,C_S_AXI_CTRL_ADDR_WIDTH=6,C_S_AXI_CTRL_DATA_WIDTH=32,C_M_AXI_DATA_IN_ID_WIDTH=1,C_M_AXI_DATA_IN_ADDR_WIDTH=64,C_M_AXI_DATA_IN_DATA_WIDTH=32,C_M_AXI_DATA_IN_AWUSER_WIDTH=1,C_M_AXI_DATA_IN_ARUSER_WIDTH=1,C_M_AXI_DATA_IN_WUSER_WIDTH=1,C_M_AXI_DATA_IN_RUSER_WIDTH=1,C_M_AXI_DATA_IN_BUSER_WIDTH=1,C_M_AXI_DATA_IN_USER_VALUE=0x00000000,C_M_AXI_DATA_IN_PROT_VALUE=000,C_M_AXI_DATA_IN_CACHE_VALUE=0011}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of solar_flare_cnn_forward_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of solar_flare_cnn_forward_0_0 : entity is "HLS";
  attribute hls_module : string;
  attribute hls_module of solar_flare_cnn_forward_0_0 : entity is "yes";
end solar_flare_cnn_forward_0_0;

architecture stub of solar_flare_cnn_forward_0_0 is
  attribute syn_black_box : boolean;
  attribute black_box_pad_pin : string;
  attribute syn_black_box of stub : architecture is true;
  attribute black_box_pad_pin of stub : architecture is "s_axi_CTRL_ARADDR[5:0],s_axi_CTRL_ARREADY,s_axi_CTRL_ARVALID,s_axi_CTRL_AWADDR[5:0],s_axi_CTRL_AWREADY,s_axi_CTRL_AWVALID,s_axi_CTRL_BREADY,s_axi_CTRL_BRESP[1:0],s_axi_CTRL_BVALID,s_axi_CTRL_RDATA[31:0],s_axi_CTRL_RREADY,s_axi_CTRL_RRESP[1:0],s_axi_CTRL_RVALID,s_axi_CTRL_WDATA[31:0],s_axi_CTRL_WREADY,s_axi_CTRL_WSTRB[3:0],s_axi_CTRL_WVALID,ap_clk,ap_rst_n,interrupt,m_axi_DATA_IN_ARADDR[63:0],m_axi_DATA_IN_ARBURST[1:0],m_axi_DATA_IN_ARCACHE[3:0],m_axi_DATA_IN_ARID[0:0],m_axi_DATA_IN_ARLEN[7:0],m_axi_DATA_IN_ARLOCK[1:0],m_axi_DATA_IN_ARPROT[2:0],m_axi_DATA_IN_ARQOS[3:0],m_axi_DATA_IN_ARREADY,m_axi_DATA_IN_ARREGION[3:0],m_axi_DATA_IN_ARSIZE[2:0],m_axi_DATA_IN_ARVALID,m_axi_DATA_IN_AWADDR[63:0],m_axi_DATA_IN_AWBURST[1:0],m_axi_DATA_IN_AWCACHE[3:0],m_axi_DATA_IN_AWID[0:0],m_axi_DATA_IN_AWLEN[7:0],m_axi_DATA_IN_AWLOCK[1:0],m_axi_DATA_IN_AWPROT[2:0],m_axi_DATA_IN_AWQOS[3:0],m_axi_DATA_IN_AWREADY,m_axi_DATA_IN_AWREGION[3:0],m_axi_DATA_IN_AWSIZE[2:0],m_axi_DATA_IN_AWVALID,m_axi_DATA_IN_BID[0:0],m_axi_DATA_IN_BREADY,m_axi_DATA_IN_BRESP[1:0],m_axi_DATA_IN_BVALID,m_axi_DATA_IN_RDATA[31:0],m_axi_DATA_IN_RID[0:0],m_axi_DATA_IN_RLAST,m_axi_DATA_IN_RREADY,m_axi_DATA_IN_RRESP[1:0],m_axi_DATA_IN_RVALID,m_axi_DATA_IN_WDATA[31:0],m_axi_DATA_IN_WID[0:0],m_axi_DATA_IN_WLAST,m_axi_DATA_IN_WREADY,m_axi_DATA_IN_WSTRB[3:0],m_axi_DATA_IN_WVALID";
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of s_axi_CTRL_ARADDR : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARADDR";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of s_axi_CTRL_ARADDR : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of s_axi_CTRL_ARADDR : signal is "XIL_INTERFACENAME s_axi_CTRL, ADDR_WIDTH 6, DATA_WIDTH 32, PROTOCOL AXI4LITE, READ_WRITE_MODE READ_WRITE, FREQ_HZ 100000000, ID_WIDTH 0, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, HAS_BURST 0, HAS_LOCK 0, HAS_PROT 0, HAS_CACHE 0, HAS_QOS 0, HAS_REGION 0, HAS_WSTRB 1, HAS_BRESP 1, HAS_RRESP 1, SUPPORTS_NARROW_BURST 0, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1, MAX_BURST_LENGTH 1, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, NUM_READ_THREADS 1, NUM_WRITE_THREADS 1, RUSER_BITS_PER_BYTE 0, WUSER_BITS_PER_BYTE 0, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of s_axi_CTRL_ARREADY : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARREADY";
  attribute X_INTERFACE_INFO of s_axi_CTRL_ARVALID : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL ARVALID";
  attribute X_INTERFACE_INFO of s_axi_CTRL_AWADDR : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWADDR";
  attribute X_INTERFACE_INFO of s_axi_CTRL_AWREADY : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWREADY";
  attribute X_INTERFACE_INFO of s_axi_CTRL_AWVALID : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL AWVALID";
  attribute X_INTERFACE_INFO of s_axi_CTRL_BREADY : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL BREADY";
  attribute X_INTERFACE_INFO of s_axi_CTRL_BRESP : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL BRESP";
  attribute X_INTERFACE_INFO of s_axi_CTRL_BVALID : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL BVALID";
  attribute X_INTERFACE_INFO of s_axi_CTRL_RDATA : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL RDATA";
  attribute X_INTERFACE_INFO of s_axi_CTRL_RREADY : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL RREADY";
  attribute X_INTERFACE_INFO of s_axi_CTRL_RRESP : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL RRESP";
  attribute X_INTERFACE_INFO of s_axi_CTRL_RVALID : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL RVALID";
  attribute X_INTERFACE_INFO of s_axi_CTRL_WDATA : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL WDATA";
  attribute X_INTERFACE_INFO of s_axi_CTRL_WREADY : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL WREADY";
  attribute X_INTERFACE_INFO of s_axi_CTRL_WSTRB : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL WSTRB";
  attribute X_INTERFACE_INFO of s_axi_CTRL_WVALID : signal is "xilinx.com:interface:aximm:1.0 s_axi_CTRL WVALID";
  attribute X_INTERFACE_INFO of ap_clk : signal is "xilinx.com:signal:clock:1.0 ap_clk CLK";
  attribute X_INTERFACE_MODE of ap_clk : signal is "slave";
  attribute X_INTERFACE_PARAMETER of ap_clk : signal is "XIL_INTERFACENAME ap_clk, ASSOCIATED_BUSIF s_axi_CTRL:m_axi_DATA_IN, ASSOCIATED_RESET ap_rst_n, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of ap_rst_n : signal is "xilinx.com:signal:reset:1.0 ap_rst_n RST";
  attribute X_INTERFACE_MODE of ap_rst_n : signal is "slave";
  attribute X_INTERFACE_PARAMETER of ap_rst_n : signal is "XIL_INTERFACENAME ap_rst_n, POLARITY ACTIVE_LOW, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of interrupt : signal is "xilinx.com:signal:interrupt:1.0 interrupt INTERRUPT";
  attribute X_INTERFACE_MODE of interrupt : signal is "master";
  attribute X_INTERFACE_PARAMETER of interrupt : signal is "XIL_INTERFACENAME interrupt, SENSITIVITY LEVEL_HIGH, PortWidth 1";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARADDR : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARADDR";
  attribute X_INTERFACE_MODE of m_axi_DATA_IN_ARADDR : signal is "master";
  attribute X_INTERFACE_PARAMETER of m_axi_DATA_IN_ARADDR : signal is "XIL_INTERFACENAME m_axi_DATA_IN, NUM_READ_OUTSTANDING 16, NUM_WRITE_OUTSTANDING 16, MAX_READ_BURST_LENGTH 16, MAX_WRITE_BURST_LENGTH 16, MAX_BURST_LENGTH 256, PROTOCOL AXI4, READ_WRITE_MODE READ_ONLY, HAS_BURST 0, SUPPORTS_NARROW_BURST 0, ADDR_WIDTH 64, DATA_WIDTH 32, FREQ_HZ 100000000, ID_WIDTH 1, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, HAS_LOCK 1, HAS_PROT 1, HAS_CACHE 1, HAS_QOS 1, HAS_REGION 1, HAS_WSTRB 1, HAS_BRESP 1, HAS_RRESP 1, PHASE 0.0, CLK_DOMAIN solar_flare_processing_system7_0_0_FCLK_CLK0, NUM_READ_THREADS 1, NUM_WRITE_THREADS 1, RUSER_BITS_PER_BYTE 0, WUSER_BITS_PER_BYTE 0, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARBURST : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARBURST";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARCACHE : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARCACHE";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARLEN : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARLEN";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARLOCK : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARLOCK";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARPROT : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARPROT";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARQOS : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARQOS";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARREADY : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARREADY";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARREGION : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARREGION";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARSIZE : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARSIZE";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_ARVALID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN ARVALID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWADDR : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWADDR";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWBURST : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWBURST";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWCACHE : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWCACHE";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWLEN : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWLEN";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWLOCK : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWLOCK";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWPROT : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWPROT";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWQOS : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWQOS";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWREADY : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWREADY";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWREGION : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWREGION";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWSIZE : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWSIZE";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_AWVALID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN AWVALID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_BID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_BREADY : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BREADY";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_BRESP : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BRESP";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_BVALID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN BVALID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_RDATA : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RDATA";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_RID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_RLAST : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RLAST";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_RREADY : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RREADY";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_RRESP : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RRESP";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_RVALID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN RVALID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_WDATA : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WDATA";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_WID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WID";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_WLAST : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WLAST";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_WREADY : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WREADY";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_WSTRB : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WSTRB";
  attribute X_INTERFACE_INFO of m_axi_DATA_IN_WVALID : signal is "xilinx.com:interface:aximm:1.0 m_axi_DATA_IN WVALID";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of stub : architecture is "cnn_forward,Vivado 2026.1";
begin
end;
