// ============================================================================
// CustomCNN1D INT8 — Bit-Exact HLS Inference Engine
//
// Reproduces the exact integer arithmetic from:
//   models/quantization.py  (IntegerConv1d, IntegerLinear, requantize, etc.)
//   models/custom_cnn1d_int8.py  (CustomCNN1D_INT8 forward pass)
//
// No floating-point operations. No approximations.
// ============================================================================
#include "cnn_hw.h"

// ============================================================================
// Requantize: INT32 accumulator -> INT8
//
// Exact replica of models/quantization.py requantize():
//   acc = acc_int32 * multiplier          (in int64 to prevent overflow)
//   if shift > 0:
//       acc = acc + (1 << (shift - 1))    (rounding offset)
//       acc = acc >> shift                (arithmetic right-shift)
//   return clamp(acc, -128, 127)
// ============================================================================
static ap_int<8> requantize(ap_int<32> acc, ap_int<32> multiplier, ap_int<32> shift) {
    #pragma HLS INLINE off
    #pragma HLS PIPELINE off
    // 64-bit intermediate to prevent overflow: 32-bit * 32-bit can exceed 32 bits
    ap_int<64> acc64 = (ap_int<64>)acc * (ap_int<64>)multiplier;

    if (shift > 0) {
        ap_int<64> rounding_offset = ((ap_int<64>)1 << (shift - 1));
        acc64 = acc64 + rounding_offset;
        // Arithmetic right-shift on signed ap_int matches Python's >> on negative ints
        acc64 = acc64 >> shift;
    }

    // Saturate to INT8 range [-128, 127]
    if (acc64 > 127) acc64 = 127;
    else if (acc64 < -128) acc64 = -128;

    return (ap_int<8>)acc64;
}

// ============================================================================
// Depthwise Conv1d (bias=False)
//
// All 4 DW layers are constructed with bias=False:
//   custom_cnn1d_int8.py lines 10, 16, 22, 28
//
// Weight shape: [IN_C, 1, K] flattened to [IN_C * K]
// Index: weight[c * K + k] accesses w[c, 0, k]
//
// Padding: zero-padding (value=0) per quantization.py line 110
// Accumulator initialized to 0 (no bias) per quantization.py line 113
// ============================================================================
template<int IN_C, int IN_L, int K, int S, int P>
void depthwise_conv1d(
    const ap_int<8> in[IN_C * IN_L],
    const ap_int<8> *weight,
    const ap_int<32> mult,
    const ap_int<32> shift,
    ap_int<8> out[IN_C * ((IN_L + 2*P - K)/S + 1)]
) {
    const int OUT_L = (IN_L + 2*P - K)/S + 1;
    for (int c = 0; c < IN_C; c++) {
        for (int t = 0; t < OUT_L; t++) {
            ap_int<32> acc = 0;  // No bias for DW layers
            for (int k = 0; k < K; k++) {
                int in_t = t * S + k - P;
                ap_int<8> val = 0;  // Zero-padding
                if (in_t >= 0 && in_t < IN_L) {
                    val = in[c * IN_L + in_t];
                }
                acc += (ap_int<32>)val * (ap_int<32>)weight[c * K + k];
            }
            out[c * OUT_L + t] = requantize(acc, mult, shift);
        }
    }
}

// ============================================================================
// Pointwise Conv1d (kernel_size=1, bias=True) + optional fused ReLU
//
// Weight shape: [OUT_C, IN_C, 1] flattened to [OUT_C * IN_C]
// Index: weight[oc * IN_C + ic] accesses w[oc, ic, 0]
//
// Bias shape: [OUT_C]
//
// Fusing ReLU is mathematically equivalent to applying it separately:
//   requantize produces int8, then clamp(min=0) is the same either way.
// ============================================================================
template<int IN_C, int OUT_C, int IN_L>
void pointwise_conv1d_relu(
    const ap_int<8> in[IN_C * IN_L],
    const ap_int<8> *weight,
    const ap_int<32> *bias,
    const ap_int<32> mult,
    const ap_int<32> shift,
    const bool do_relu,
    ap_int<8> out[OUT_C * IN_L]
) {
    for (int oc = 0; oc < OUT_C; oc++) {
        for (int t = 0; t < IN_L; t++) {
            ap_int<32> acc = bias[oc];
            for (int ic = 0; ic < IN_C; ic++) {
                ap_int<8> val = in[ic * IN_L + t];
                acc += (ap_int<32>)val * (ap_int<32>)weight[oc * IN_C + ic];
            }
            ap_int<8> res = requantize(acc, mult, shift);
            if (do_relu && res < 0) res = 0;
            out[oc * IN_L + t] = res;
        }
    }
}

template<>
void pointwise_conv1d_relu<64, 128, 7>(
    const ap_int<8> in[64 * 7],
    const ap_int<8> *weight,
    const ap_int<32> *bias,
    const ap_int<32> mult,
    const ap_int<32> shift,
    const bool do_relu,
    ap_int<8> out[128 * 7]
) {
    for (int oc = 0; oc < 128; oc++) {
        for (int t = 0; t < 7; t++) {
            ap_int<32> acc = bias[oc];
            for (int ic = 0; ic < 64; ic++) {
                #pragma HLS PIPELINE off
                ap_int<8> val = in[ic * 7 + t];
                acc += (ap_int<32>)val * (ap_int<32>)weight[oc * 64 + ic];
            }
            ap_int<8> res = requantize(acc, mult, shift);
            if (do_relu && res < 0) res = 0;
            out[oc * 7 + t] = res;
        }
    }
}

// ============================================================================
// MaxPool1d (kernel_size=2, stride=2, padding=0)
//
// Matches quantization.py IntegerMaxPool1d:
//   stride defaults to kernel_size (line 185)
//   padding=0 for all pool layers
//   unfold(2, 2, 2).max(dim=-1) produces floor(IN_L/2) output positions
// ============================================================================
template<int C, int IN_L>
void maxpool1d_k2(const ap_int<8> in[C * IN_L], ap_int<8> out[C * (IN_L / 2)]) {
    const int OUT_L = IN_L / 2;
    for (int c = 0; c < C; c++) {
        for (int t = 0; t < OUT_L; t++) {
            ap_int<8> v0 = in[c * IN_L + t * 2];
            ap_int<8> v1 = in[c * IN_L + t * 2 + 1];
            out[c * OUT_L + t] = (v0 > v1) ? v0 : v1;
        }
    }
}

// ============================================================================
// Global Mean Pool
//
// Matches quantization.py IntegerMeanPool.forward():
//   acc_int32 = x_int8.to(int32).sum(dim=-1)   # sum all IN_L time steps
//   out = requantize(acc_int32, multiplier, shift)
//
// The multiplier/shift encode both (1/window_size) and scale adjustment.
// ============================================================================
template<int C, int IN_L>
void global_mean_pool(
    const ap_int<8> in[C * IN_L],
    const ap_int<32> mult,
    const ap_int<32> shift,
    ap_int<8> out[C]
) {
    for (int c = 0; c < C; c++) {
        ap_int<32> sum = 0;
        for (int t = 0; t < IN_L; t++) {
            sum += (ap_int<32>)in[c * IN_L + t];
        }
        out[c] = requantize(sum, mult, shift);
    }
}

// ============================================================================
// Global Max Pool + Concat Scaling
//
// Matches custom_cnn1d_int8.py lines 77-79:
//   x_max_int32 = x.to(torch.int32).max(dim=-1).values
//   x_max = requantize(x_max_int32, concat_max_multiplier, concat_max_shift)
//
// The requantize aligns the max pool output scale to the mean pool output
// scale so they can be safely concatenated.
// ============================================================================
template<int C, int IN_L>
void global_max_pool(
    const ap_int<8> in[C * IN_L],
    const ap_int<32> mult,
    const ap_int<32> shift,
    ap_int<8> out[C]
) {
    for (int c = 0; c < C; c++) {
        ap_int<8> max_val = -128;
        for (int t = 0; t < IN_L; t++) {
            ap_int<8> val = in[c * IN_L + t];
            if (val > max_val) max_val = val;
        }
        // max() over int8 values yields the same result as max() over their
        // int32 representations (all values fit in [-128, 127])
        out[c] = requantize((ap_int<32>)max_val, mult, shift);
    }
}

// ============================================================================
// Fully Connected Layer + optional fused ReLU
//
// Matches quantization.py IntegerLinear.forward():
//   acc = matmul(x_int32, weight_int32.t())   # x @ W^T
//   acc += bias_int32
//   out = requantize(acc, multiplier, shift)
//
// Weight shape: [OUT_C, IN_C] flattened to [OUT_C * IN_C]
// Index: weight[oc * IN_C + ic] accesses W[oc, ic]
// This matches W^T access pattern: acc[oc] = sum_ic(x[ic] * W[oc, ic])
// ============================================================================
template<int IN_C, int OUT_C>
void linear_layer(
    const ap_int<8> in[IN_C],
    const ap_int<8> *weight,
    const ap_int<32> *bias,
    const ap_int<32> mult,
    const ap_int<32> shift,
    const bool do_relu,
    ap_int<8> out[OUT_C]
) {
    for (int oc = 0; oc < OUT_C; oc++) {
        ap_int<32> acc = bias[oc];
        for (int ic = 0; ic < IN_C; ic++) {
            acc += (ap_int<32>)in[ic] * (ap_int<32>)weight[oc * IN_C + ic];
        }
        ap_int<8> res = requantize(acc, mult, shift);
        if (do_relu && res < 0) res = 0;
        out[oc] = res;
    }
}

// ============================================================================
// Top-Level Inference Function
//
// Reproduces the exact forward() from custom_cnn1d_int8.py lines 48-89.
//
// Execution order per block: DW_Conv -> PW_Conv -> ReLU -> MaxPool
// (Block 4 has no MaxPool)
// Then: MeanPool + MaxPool(with concat scaling) -> Concat -> FC1+ReLU -> FC2
// ============================================================================
void cnn_forward(const ap_int<8> input[24 * 60], ap_int<8> *output_logit) {
    #pragma HLS INTERFACE s_axilite port=return bundle=CTRL
    #pragma HLS INTERFACE m_axi port=input bundle=DATA_IN depth=1440
    #pragma HLS INTERFACE s_axilite port=output_logit bundle=CTRL

    // ===== Block 1 =====
    // b1_dw: DW Conv(24->24, K=3, S=1, P=1, G=24, bias=False) -> [24, 60]
    ap_int<8> buf_b1_dw[24 * 60];
    depthwise_conv1d<24, 60, 3, 1, 1>(input, b1_dw_weight,
        B1_DW_MULTIPLIER, B1_DW_SHIFT, buf_b1_dw);

    // b1_pw: PW Conv(24->24, K=1, bias=True) + ReLU -> [24, 60]
    ap_int<8> buf_b1_pw[24 * 60];
    pointwise_conv1d_relu<24, 24, 60>(buf_b1_dw, b1_pw_weight, b1_pw_bias,
        B1_PW_MULTIPLIER, B1_PW_SHIFT, true, buf_b1_pw);

    // b1_pool: MaxPool(K=2, S=2) -> [24, 30]
    ap_int<8> buf_b1_pool[24 * 30];
    maxpool1d_k2<24, 60>(buf_b1_pw, buf_b1_pool);

    // ===== Block 2 =====
    // b2_dw: DW Conv(24->24, K=3, S=1, P=1, G=24, bias=False) -> [24, 30]
    ap_int<8> buf_b2_dw[24 * 30];
    depthwise_conv1d<24, 30, 3, 1, 1>(buf_b1_pool, b2_dw_weight,
        B2_DW_MULTIPLIER, B2_DW_SHIFT, buf_b2_dw);

    // b2_pw: PW Conv(24->32, K=1, bias=True) + ReLU -> [32, 30]
    ap_int<8> buf_b2_pw[32 * 30];
    pointwise_conv1d_relu<24, 32, 30>(buf_b2_dw, b2_pw_weight, b2_pw_bias,
        B2_PW_MULTIPLIER, B2_PW_SHIFT, true, buf_b2_pw);

    // b2_pool: MaxPool(K=2, S=2) -> [32, 15]
    ap_int<8> buf_b2_pool[32 * 15];
    maxpool1d_k2<32, 30>(buf_b2_pw, buf_b2_pool);

    // ===== Block 3 =====
    // b3_dw: DW Conv(32->32, K=3, S=1, P=1, G=32, bias=False) -> [32, 15]
    ap_int<8> buf_b3_dw[32 * 15];
    depthwise_conv1d<32, 15, 3, 1, 1>(buf_b2_pool, b3_dw_weight,
        B3_DW_MULTIPLIER, B3_DW_SHIFT, buf_b3_dw);

    // b3_pw: PW Conv(32->64, K=1, bias=True) + ReLU -> [64, 15]
    ap_int<8> buf_b3_pw[64 * 15];
    pointwise_conv1d_relu<32, 64, 15>(buf_b3_dw, b3_pw_weight, b3_pw_bias,
        B3_PW_MULTIPLIER, B3_PW_SHIFT, true, buf_b3_pw);

    // b3_pool: MaxPool(K=2, S=2) -> [64, 7]
    ap_int<8> buf_b3_pool[64 * 7];
    maxpool1d_k2<64, 15>(buf_b3_pw, buf_b3_pool);

    // ===== Block 4 =====
    // b4_dw: DW Conv(64->64, K=3, S=1, P=1, G=64, bias=False) -> [64, 7]
    ap_int<8> buf_b4_dw[64 * 7];
    depthwise_conv1d<64, 7, 3, 1, 1>(buf_b3_pool, b4_dw_weight,
        B4_DW_MULTIPLIER, B4_DW_SHIFT, buf_b4_dw);

    // b4_pw: PW Conv(64->128, K=1, bias=True) + ReLU -> [128, 7]
    ap_int<8> buf_b4_pw[128 * 7];
    pointwise_conv1d_relu<64, 128, 7>(buf_b4_dw, b4_pw_weight, b4_pw_bias,
        B4_PW_MULTIPLIER, B4_PW_SHIFT, true, buf_b4_pw);

    // ===== Global Pooling =====
    // mean_pool: sum all 7 time steps per channel, then requantize -> [128]
    ap_int<8> buf_mean_pool[128];
    global_mean_pool<128, 7>(buf_b4_pw,
        MEAN_POOL_MULTIPLIER, MEAN_POOL_SHIFT, buf_mean_pool);

    // global max pool: max over 7 time steps, then requantize for concat alignment -> [128]
    ap_int<8> buf_max_pool[128];
    global_max_pool<128, 7>(buf_b4_pw,
        GLOBAL_MAX_POOL_MULTIPLIER, GLOBAL_MAX_POOL_SHIFT, buf_max_pool);

    // ===== Concatenation =====
    // cat([x_mean, x_max], dim=1) -> [256]
    // Mean at indices [0..127], Max at indices [128..255]
    ap_int<8> buf_concat[256];
    for (int i = 0; i < 128; i++) {
        buf_concat[i] = buf_mean_pool[i];
        buf_concat[128 + i] = buf_max_pool[i];
    }

    // ===== Classifier =====
    // fc1: Linear(256->32, bias=True) + ReLU -> [32]
    ap_int<8> buf_fc1[32];
    linear_layer<256, 32>(buf_concat, fc1_weight, fc1_bias,
        FC1_MULTIPLIER, FC1_SHIFT, true, buf_fc1);

    // fc2: Linear(32->1, bias=True), no ReLU -> [1]
    ap_int<8> buf_fc2[1];
    linear_layer<32, 1>(buf_fc1, fc2_weight, fc2_bias,
        FC2_MULTIPLIER, FC2_SHIFT, false, buf_fc2);

    *output_logit = buf_fc2[0];
}
