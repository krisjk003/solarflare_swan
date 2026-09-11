// ============================================================================
// CustomCNN1D INT8 — HLS Testbench
//
// Calls cnn_forward() with a test input and compares against a known
// PyTorch INT8 output to verify bit-exactness.
//
// To generate test vectors from PyTorch, run something like:
//
//   import torch
//   from models.custom_cnn1d_int8 import CustomCNN1D_INT8
//   from models.quantization import quantize_int8
//
//   model = CustomCNN1D_INT8()
//   ckpt = torch.load("checkpoints/int8_real/custom_cnn1d_int8_real.pt",
//                      map_location="cpu", weights_only=False)
//   model.load_state_dict(ckpt['model_state_dict'])
//   model.eval()
//
//   # Use a real preprocessed+quantized sample, or a deterministic pattern:
//   x_float = torch.randn(1, 24, 60)
//   x_int8 = quantize_int8(x_float, model.input_scale.item())
//   y_int8 = model(x_int8)
//
//   # Save input
//   with open("hls/test_input.txt", "w") as f:
//       for v in x_int8.flatten().tolist():
//           f.write(f"{int(v)}\n")
//
//   # Save expected output
//   with open("hls/test_expected.txt", "w") as f:
//       f.write(f"{int(y_int8.item())}\n")
//
// ============================================================================
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <string>
#include "cnn_hw.h"

// Helper to resolve paths relative to this source file, independent of CWD
std::string get_test_file_path(const std::string& filename) {
    std::string src_path = __FILE__;
    size_t pos = src_path.find_last_of("\\/");
    if (pos != std::string::npos) {
        return src_path.substr(0, pos + 1) + filename;
    }
    return filename;
}

int main() {
    ap_int<8> test_input[MODEL_INPUT_CHANNELS * MODEL_INPUT_LENGTH];
    ap_int<8> output_logit = 0;

    // ---- Load test input from file ----
    std::string input_path = get_test_file_path("test_input.txt");
    std::ifstream fin(input_path.c_str());
    if (fin.is_open()) {
        for (int i = 0; i < MODEL_INPUT_CHANNELS * MODEL_INPUT_LENGTH; i++) {
            int val;
            fin >> val;
            test_input[i] = (ap_int<8>)val;
        }
        fin.close();
        std::cout << "Loaded test input from " << input_path << std::endl;
    } else {
        std::cerr << "ERROR: test_input.txt not found at " << input_path << std::endl;
        return 1;
    }

    // ---- Run hardware inference ----
    cnn_forward(test_input, &output_logit);
    std::cout << "HLS output logit (INT8): " << (int)output_logit << std::endl;

    // ---- Compare against expected PyTorch output ----
    std::string expected_path = get_test_file_path("test_expected.txt");
    std::ifstream fexp(expected_path.c_str());
    if (fexp.is_open()) {
        int expected;
        fexp >> expected;
        fexp.close();

        if ((int)output_logit == expected) {
            std::cout << "PASS: HLS output matches PyTorch INT8 output ("
                      << expected << ")." << std::endl;
            return 0;
        } else {
            std::cout << "FAIL: HLS output = " << (int)output_logit
                      << ", expected = " << expected << std::endl;
            return 1;
        }
    } else {
        std::cerr << "ERROR: test_expected.txt not found at " << expected_path << std::endl;
        return 1;
    }
}
