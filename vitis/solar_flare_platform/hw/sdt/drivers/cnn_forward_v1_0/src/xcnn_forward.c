// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1 (64-bit)
// Tool Version Limit: 2026.06
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
/***************************** Include Files *********************************/
#include "xcnn_forward.h"

/************************** Function Implementation *************************/
#ifndef __linux__
int XCnn_forward_CfgInitialize(XCnn_forward *InstancePtr, XCnn_forward_Config *ConfigPtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    InstancePtr->Ctrl_BaseAddress = ConfigPtr->Ctrl_BaseAddress;
    InstancePtr->IsReady = XIL_COMPONENT_IS_READY;

    return XST_SUCCESS;
}
#endif

void XCnn_forward_Start(XCnn_forward *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_AP_CTRL) & 0x80;
    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_AP_CTRL, Data | 0x01);
}

u32 XCnn_forward_IsDone(XCnn_forward *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_AP_CTRL);
    return (Data >> 1) & 0x1;
}

u32 XCnn_forward_IsIdle(XCnn_forward *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_AP_CTRL);
    return (Data >> 2) & 0x1;
}

u32 XCnn_forward_IsReady(XCnn_forward *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_AP_CTRL);
    // check ap_start to see if the pcore is ready for next input
    return !(Data & 0x1);
}

void XCnn_forward_EnableAutoRestart(XCnn_forward *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_AP_CTRL, 0x80);
}

void XCnn_forward_DisableAutoRestart(XCnn_forward *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_AP_CTRL, 0);
}

void XCnn_forward_Set_input_r(XCnn_forward *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_INPUT_R_DATA, (u32)(Data));
    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_INPUT_R_DATA + 4, (u32)(Data >> 32));
}

u64 XCnn_forward_Get_input_r(XCnn_forward *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_INPUT_R_DATA);
    Data += (u64)XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_INPUT_R_DATA + 4) << 32;
    return Data;
}

u32 XCnn_forward_Get_output_logit(XCnn_forward *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_OUTPUT_LOGIT_DATA);
    return Data;
}

u32 XCnn_forward_Get_output_logit_vld(XCnn_forward *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_OUTPUT_LOGIT_CTRL);
    return Data & 0x1;
}

void XCnn_forward_InterruptGlobalEnable(XCnn_forward *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_GIE, 1);
}

void XCnn_forward_InterruptGlobalDisable(XCnn_forward *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_GIE, 0);
}

void XCnn_forward_InterruptEnable(XCnn_forward *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_IER);
    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_IER, Register | Mask);
}

void XCnn_forward_InterruptDisable(XCnn_forward *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_IER);
    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_IER, Register & (~Mask));
}

void XCnn_forward_InterruptClear(XCnn_forward *InstancePtr, u32 Mask) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XCnn_forward_WriteReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_ISR, Mask);
}

u32 XCnn_forward_InterruptGetEnabled(XCnn_forward *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_IER);
}

u32 XCnn_forward_InterruptGetStatus(XCnn_forward *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XCnn_forward_ReadReg(InstancePtr->Ctrl_BaseAddress, XCNN_FORWARD_CTRL_ADDR_ISR);
}

