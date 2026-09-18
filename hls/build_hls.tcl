# ============================================================================
# CustomCNN1D INT8 — Vitis 2026.1 HLS Build Script (TCL Legacy Flow)
#
# USAGE (from project root):
#
#   source /opt/Xilinx/2026.1/Vitis/settings64.sh
#   vitis-run --mode hls --tcl hls/build_hls.tcl
#
# NOTE: The standalone 'vitis_hls' binary no longer ships with Vitis 2026.1.
#       Use 'vitis-run --mode hls --tcl' to evaluate HLS TCL scripts.
#       Alternatively, use the config-driven flow with hls/hls_config.cfg
#       (see that file for details).
#
# This script configures the HLS project but does NOT auto-run synthesis.
# Uncomment the commands at the bottom to run csim, csynth, or IP export.
# ============================================================================

open_project cnn_hls_project

set_top cnn_forward

# Source files (paths relative to where vitis-run is invoked, i.e. project root)
add_files hls/cnn_hw.cpp
add_files -tb hls/cnn_tb.cpp

open_solution "solution1"

# ============================================================================
# TARGET FPGA PART — EBAZ4205
#
# Board:  EBAZ4205 (Zynq-7000 SoC)
# FPGA:   XC7Z010CLG400-1
# ============================================================================
set_part {xc7z010clg400-1}

# 10 ns clock = 100 MHz (conservative starting point)
create_clock -period 10 -name default

# ============================================================================
# Uncomment the following lines to execute synthesis steps:
#
# C Simulation (verify functional correctness against testbench):
# csim_design
#
# C Synthesis (generate RTL from HLS C++):
# csynth_design
#
# Co-Simulation (verify RTL matches C simulation):
# cosim_design
#
# Export IP for Vivado integration:
# export_design -format ip_catalog
# ============================================================================

exit
