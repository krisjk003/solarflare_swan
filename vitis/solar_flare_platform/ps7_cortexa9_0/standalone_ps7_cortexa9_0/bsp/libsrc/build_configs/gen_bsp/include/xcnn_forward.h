// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1 (64-bit)
// Tool Version Limit: 2026.06
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
#ifndef XCNN_FORWARD_H
#define XCNN_FORWARD_H

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files *********************************/
#ifndef __linux__
#include "xil_types.h"
#include "xil_assert.h"
#include "xstatus.h"
#include "xil_io.h"
#else
#include <stdint.h>
#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stddef.h>
#endif
#include "xcnn_forward_hw.h"

/**************************** Type Definitions ******************************/
#ifdef __linux__
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#else
typedef struct {
#ifdef SDT
    char *Name;
#else
    u16 DeviceId;
#endif
    u64 Ctrl_BaseAddress;
} XCnn_forward_Config;
#endif

typedef struct {
    u64 Ctrl_BaseAddress;
    u32 IsReady;
} XCnn_forward;

typedef u32 word_type;

/***************** Macros (Inline Functions) Definitions *********************/
#ifndef __linux__
#define XCnn_forward_WriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define XCnn_forward_ReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
#else
#define XCnn_forward_WriteReg(BaseAddress, RegOffset, Data) \
    *(volatile u32*)((BaseAddress) + (RegOffset)) = (u32)(Data)
#define XCnn_forward_ReadReg(BaseAddress, RegOffset) \
    *(volatile u32*)((BaseAddress) + (RegOffset))

#define Xil_AssertVoid(expr)    assert(expr)
#define Xil_AssertNonvoid(expr) assert(expr)

#define XST_SUCCESS             0
#define XST_DEVICE_NOT_FOUND    2
#define XST_OPEN_DEVICE_FAILED  3
#define XIL_COMPONENT_IS_READY  1
#endif

/************************** Function Prototypes *****************************/
#ifndef __linux__
#ifdef SDT
int XCnn_forward_Initialize(XCnn_forward *InstancePtr, UINTPTR BaseAddress);
XCnn_forward_Config* XCnn_forward_LookupConfig(UINTPTR BaseAddress);
#else
int XCnn_forward_Initialize(XCnn_forward *InstancePtr, u16 DeviceId);
XCnn_forward_Config* XCnn_forward_LookupConfig(u16 DeviceId);
#endif
int XCnn_forward_CfgInitialize(XCnn_forward *InstancePtr, XCnn_forward_Config *ConfigPtr);
#else
int XCnn_forward_Initialize(XCnn_forward *InstancePtr, const char* InstanceName);
int XCnn_forward_Release(XCnn_forward *InstancePtr);
#endif

void XCnn_forward_Start(XCnn_forward *InstancePtr);
u32 XCnn_forward_IsDone(XCnn_forward *InstancePtr);
u32 XCnn_forward_IsIdle(XCnn_forward *InstancePtr);
u32 XCnn_forward_IsReady(XCnn_forward *InstancePtr);
void XCnn_forward_EnableAutoRestart(XCnn_forward *InstancePtr);
void XCnn_forward_DisableAutoRestart(XCnn_forward *InstancePtr);

void XCnn_forward_Set_input_r(XCnn_forward *InstancePtr, u64 Data);
u64 XCnn_forward_Get_input_r(XCnn_forward *InstancePtr);
u32 XCnn_forward_Get_output_logit(XCnn_forward *InstancePtr);
u32 XCnn_forward_Get_output_logit_vld(XCnn_forward *InstancePtr);

void XCnn_forward_InterruptGlobalEnable(XCnn_forward *InstancePtr);
void XCnn_forward_InterruptGlobalDisable(XCnn_forward *InstancePtr);
void XCnn_forward_InterruptEnable(XCnn_forward *InstancePtr, u32 Mask);
void XCnn_forward_InterruptDisable(XCnn_forward *InstancePtr, u32 Mask);
void XCnn_forward_InterruptClear(XCnn_forward *InstancePtr, u32 Mask);
u32 XCnn_forward_InterruptGetEnabled(XCnn_forward *InstancePtr);
u32 XCnn_forward_InterruptGetStatus(XCnn_forward *InstancePtr);

#ifdef __cplusplus
}
#endif

#endif
