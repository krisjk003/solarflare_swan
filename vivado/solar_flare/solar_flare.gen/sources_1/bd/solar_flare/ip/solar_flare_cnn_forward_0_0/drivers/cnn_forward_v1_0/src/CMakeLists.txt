# ==============================================================
# Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1 (64-bit)
# Tool Version Limit: 2026.06
# Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
# Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
# 
# ==============================================================
cmake_minimum_required(VERSION 3.15)
project(cnn_forward)
find_package(common)
collector_create (PROJECT_LIB_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}")
collect (PROJECT_LIB_SOURCES xcnn_forward.c)
collect (PROJECT_LIB_SOURCES xcnn_forward_sinit.c)
collect (PROJECT_LIB_SOURCES xcnn_forward_linux.c)
collect (PROJECT_LIB_SOURCES xcnn_forward_g.c)
collector_list (_sources PROJECT_LIB_SOURCES)
collector_create (PROJECT_LIB_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}")
collect (PROJECT_LIB_HEADERS xcnn_forward.h)
collect (PROJECT_LIB_HEADERS xcnn_forward_hw.h)
collector_list (_headers PROJECT_LIB_HEADERS)
file(COPY ${_headers} DESTINATION ${CMAKE_BINARY_DIR}/include)
include_directories(${CMAKE_BINARY_DIR}/include)
add_library(cnn_forward STATIC ${_sources})
set_target_properties(cnn_forward PROPERTIES LINKER_LANGUAGE C)

