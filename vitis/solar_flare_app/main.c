#include "xparameters.h"
#include "xcnn_forward.h"
#include "xil_printf.h"
#include "xil_cache.h"
#include "xstatus.h"

#define INPUT_SIZE 1440

/* Test input: 1440 INT8 values */
static signed char input_data[INPUT_SIZE];

int main(void)
{
    XCnn_forward cnn;
    int status;

    xil_printf("\r\n=================================\r\n");
    xil_printf(" Solar Flare CNN FPGA Test\r\n");
    xil_printf("=================================\r\n");

    /* Initialize test input */
    for (int i = 0; i < INPUT_SIZE; i++) {
        input_data[i] = 0;
    }

    /*
     * Flush CPU cache so the AXI master in the PL
     * sees the latest DDR contents.
     */
    Xil_DCacheFlushRange((UINTPTR)input_data, sizeof(input_data));

    /* Initialize CNN hardware driver */
    status = XCnn_forward_Initialize(
        &cnn,
        XPAR_CNN_FORWARD_0_BASEADDR
    );

    if (status != XST_SUCCESS) {
        xil_printf("ERROR: CNN initialization failed: %d\r\n", status);
        return XST_FAILURE;
    }

    xil_printf("CNN driver initialized.\r\n");
    xil_printf("CNN base address: 0x%08X\r\n",
               XPAR_CNN_FORWARD_0_BASEADDR);

    /* Give accelerator the DDR address of input_data */
    XCnn_forward_Set_input_r(
        &cnn,
        (u64)(UINTPTR)input_data
    );

    xil_printf("Input buffer address: 0x%08X\r\n",
               (UINTPTR)input_data);

    xil_printf("Starting CNN...\r\n");

    XCnn_forward_Start(&cnn);

    /* Wait for hardware accelerator */
    while (!XCnn_forward_IsDone(&cnn)) {
        ;
    }

    xil_printf("CNN execution complete.\r\n");

    /* Read output logit */
    u32 result = XCnn_forward_Get_output_logit(&cnn);

    xil_printf("Output logit: %d\r\n", (signed char)result);

    xil_printf("=================================\r\n");

    return XST_SUCCESS;
}