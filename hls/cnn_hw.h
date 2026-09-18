#pragma once

#include <ap_int.h>

// Include the exported INT8 weights, biases, multipliers, and shifts
// Path is relative to this header file's location (hls/)
#include "../results/int8_real/hls/weights.h"

// ============================================================================
// Top-level synthesizable function for the CustomCNN1D INT8 inference engine.
//
// Input:  1440 elements (24 channels x 60 time steps), flattened row-major.
//         Layout: input[c * 60 + t] for channel c, time step t.
// Output: Single INT8 logit (pre-sigmoid).
// ============================================================================
void cnn_forward(
    const ap_int<8> input[MODEL_INPUT_CHANNELS * MODEL_INPUT_LENGTH],
    ap_int<8> *output_logit
);
