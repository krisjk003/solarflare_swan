import os
import sys
import json
import unittest
from unittest.mock import patch
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.quantization import (
    quantize_int7, dequantize_int7, calculate_symmetric_scale,
    quantize_bias_int32, requantize, IntegerConv1d, IntegerLinear,
    IntegerReLU, IntegerMaxPool1d, IntegerMeanPool, compute_multiplier_shift
)
from models.custom_cnn1d_int7 import CustomCNN1D_INT7
from models.custom_cnn1d import CustomCNN1D
from scripts.quantize import build_fused_fp32_model, run_calibration, convert_to_int7, prepare_calibration_data
from scripts.export_hls import export_hls_from_model

class TestIntegerOperators(unittest.TestCase):
    def test_1_integer_conv1d_manual_reference(self):
        # Manually verify 1D convolution with known integer values
        # Input: B=1, C_in=1, L=4: [10, 20, 30, 40]
        # Weight: C_out=1, in_per_group=1, K=2: [2, 3]
        # Valid output (stride=1, padding=0):
        # pos 0: 10*2 + 20*3 = 20 + 60 = 80
        # pos 1: 20*2 + 30*3 = 40 + 90 = 130
        # pos 2: 30*2 + 40*3 = 60 + 120 = 180
        conv = IntegerConv1d(in_channels=1, out_channels=1, kernel_size=2, stride=1, padding=0, bias=False)
        conv.weight_int7.data = torch.tensor([[[2, 3]]], dtype=torch.int8)
        # Identity requantization: multiplier=1, shift=0
        conv.multiplier.data = torch.tensor(1, dtype=torch.int32)
        conv.shift.data = torch.tensor(0, dtype=torch.int32)
        
        x = torch.tensor([[[10, 20, 30, 40]]], dtype=torch.int8)
        out = conv(x)
        # Since output clamps to 63, let's use a scale factor or test accumulator directly
        # With multiplier=1, shift=1: 80>>1=40, 130>>1=65->clamped 63, etc.
        # Or with multiplier=1, shift=2:
        # 80/4 = 20, 130/4 = 32.5 (rounded 33), 180/4 = 45
        conv.shift.data = torch.tensor(2, dtype=torch.int32)
        out = conv(x)
        self.assertEqual(out.tolist(), [[[20, 33, 45]]])
        self.assertEqual(out.dtype, torch.int8)

    def test_2_integer_linear_manual_reference(self):
        # Input: B=1, in_features=3: [2, -3, 4]
        # Weight: out_features=2, in_features=3: [[1, 2, 3], [-2, 0, 1]]
        # Row 0: 2*1 + (-3)*2 + 4*3 = 2 - 6 + 12 = 8
        # Row 1: 2*(-2) + (-3)*0 + 4*1 = -4 + 0 + 4 = 0
        linear = IntegerLinear(in_features=3, out_features=2, bias=False)
        linear.weight_int7.data = torch.tensor([[1, 2, 3], [-2, 0, 1]], dtype=torch.int8)
        linear.multiplier.data = torch.tensor(1, dtype=torch.int32)
        linear.shift.data = torch.tensor(0, dtype=torch.int32)
        
        x = torch.tensor([[2, -3, 4]], dtype=torch.int8)
        out = linear(x)
        self.assertEqual(out.tolist(), [[8, 0]])
        self.assertEqual(out.dtype, torch.int8)

    def test_3_integer_maxpool_reference(self):
        # Input: B=1, C=1, L=6: [-5, 12, 63, -64, 0, 3]
        # kernel_size=2, stride=2 -> max(-5, 12)=12, max(63, -64)=63, max(0, 3)=3
        pool = IntegerMaxPool1d(kernel_size=2, stride=2)
        x = torch.tensor([[[-5, 12, 63, -64, 0, 3]]], dtype=torch.int8)
        out = pool(x)
        self.assertEqual(out.tolist(), [[[12, 63, 3]]])
        self.assertEqual(out.dtype, torch.int8)

    def test_4_int32_bias_addition(self):
        # Conv with bias: acc = 80, bias = 100 -> acc = 180
        # shift=2 -> round(180/4) = 45
        conv = IntegerConv1d(in_channels=1, out_channels=1, kernel_size=2, stride=1, padding=0, bias=True)
        conv.weight_int7.data = torch.tensor([[[2, 3]]], dtype=torch.int8)
        conv.bias_int32.data = torch.tensor([100], dtype=torch.int32)
        conv.multiplier.data = torch.tensor(1, dtype=torch.int32)
        conv.shift.data = torch.tensor(2, dtype=torch.int32)
        
        x = torch.tensor([[[10, 20]]], dtype=torch.int8)
        out = conv(x)
        # 10*2 + 20*3 + 100 = 20 + 60 + 100 = 180. 180 >> 2 = 45
        self.assertEqual(out.item(), 45)

    def test_5_requantization_correctness(self):
        # Check clamping to [-64, 63]
        acc_pos = torch.tensor([1000], dtype=torch.int32)
        out_pos = requantize(acc_pos, multiplier=1, shift=0)
        self.assertEqual(out_pos.item(), 63)
        
        acc_neg = torch.tensor([-1000], dtype=torch.int32)
        out_neg = requantize(acc_neg, multiplier=1, shift=0)
        self.assertEqual(out_neg.item(), -64)
        
        # Check round-to-nearest with shift
        # 5 >> 1 with rounding: (5 + 1) >> 1 = 3
        acc = torch.tensor([5], dtype=torch.int32)
        out = requantize(acc, multiplier=1, shift=1)
        self.assertEqual(out.item(), 3)

    def test_6_depthwise_groups(self):
        # Depthwise conv with groups=24
        # Channel c must only depend on input channel c
        conv = IntegerConv1d(in_channels=24, out_channels=24, kernel_size=3, padding=1, groups=24, bias=False)
        conv.weight_int7.data.fill_(0)
        # Set channel 5 weight to 1
        conv.weight_int7.data[5, 0, 1] = 1 # center tap
        conv.multiplier.data = torch.tensor(1, dtype=torch.int32)
        conv.shift.data = torch.tensor(0, dtype=torch.int32)
        
        x = torch.zeros((1, 24, 10), dtype=torch.int8)
        x[0, 5, :] = 42
        x[0, 3, :] = 99 # should not affect channel 5
        
        out = conv(x)
        self.assertTrue(torch.all(out[0, 5, :] == 42))
        self.assertTrue(torch.all(out[0, 3, :] == 0))

    def test_7_end_to_end_custom_cnn1d_int7(self):
        model = CustomCNN1D_INT7(in_channels=24)
        x = torch.randint(-64, 63, (2, 24, 60), dtype=torch.int8)
        out = model(x)
        self.assertEqual(out.shape, (2, 1))
        self.assertEqual(out.dtype, torch.int8)
        self.assertTrue((out >= -64).all() and (out <= 63).all())

    def test_8_hls_metadata_completeness(self):
        model = CustomCNN1D_INT7(in_channels=24)
        header_path, json_path = export_hls_from_model(model, out_dir="results/hls_export")
        self.assertTrue(os.path.exists(header_path))
        self.assertTrue(os.path.exists(json_path))
        
        with open(json_path, "r") as jf:
            meta = json.load(jf)
            
        self.assertEqual(meta["model_name"], "CustomCNN1D_INT7")
        self.assertEqual(meta["input_dimensions"], [24, 60])
        self.assertIn("layers", meta)
        
        # Verify layer metadata contains all required keys
        required_keys = [
            "layer_name", "operation_type", "input_dimensions", "output_dimensions"
        ]
        conv_required_keys = [
            "input_channels", "output_channels", "kernel_size", "stride",
            "padding", "dilation", "groups", "input_scale", "weight_scale",
            "output_scale", "multiplier", "shift", "bias_info"
        ]
        for layer in meta["layers"]:
            for k in required_keys:
                self.assertIn(k, layer)
            if "Conv1d" in layer["operation_type"] or layer["operation_type"] == "Linear":
                for k in conv_required_keys:
                    self.assertIn(k, layer)

    def test_9_no_fp32_kernels_called_in_integer_path(self):
        # Patch F.conv1d, F.linear, F.max_pool1d to raise error if called
        with patch('torch.nn.functional.conv1d', side_effect=RuntimeError("F.conv1d called!")):
            with patch('torch.nn.functional.linear', side_effect=RuntimeError("F.linear called!")):
                with patch('torch.nn.functional.max_pool1d', side_effect=RuntimeError("F.max_pool1d called!")):
                    model = CustomCNN1D_INT7(in_channels=24)
                    x = torch.randint(-64, 63, (1, 24, 60), dtype=torch.int8)
                    # Forward pass must complete without any RuntimeError
                    out = model(x)
                    self.assertEqual(out.shape, (1, 1))

class TestCalibrationLoader(unittest.TestCase):
    @patch('scripts.quantize._get_partition_files')
    @patch('scripts.quantize.load_files_to_matrix')
    @patch('scripts.quantize.TargetExtractor.extract_binary')
    def test_calibration_loader_mocked(self, mock_extract, mock_load, mock_get):
        import numpy as np
        mock_get.return_value = (np.array(['f1.csv', 'f2.csv', 'f3.csv', 'f4.csv', 'f5.csv']), None)
        mock_load.side_effect = lambda files: np.ones((len(files), 24, 60), dtype=np.float32)
        mock_extract.return_value = 0
        
        checkpoint_prep = {
            'fallback_mean': np.zeros((24, 1)).tolist(),
            'X_min': np.zeros((24, 1)).tolist(),
            'X_max': np.ones((24, 1)).tolist()
        }
        
        loader = prepare_calibration_data('dummy_dir', '1,2,3', checkpoint_prep, max_samples=3)
        self.assertEqual(len(loader.dataset), 3)
        
        for x, y in loader:
            self.assertEqual(x.shape[1:], (24, 60))
            break
            
        with self.assertRaises(ValueError):
            prepare_calibration_data('dummy_dir', '1,2,5', checkpoint_prep, max_samples=3)
            
        mock_get.assert_called_with('dummy_dir', ['partition1', 'partition2', 'partition3'])

if __name__ == "__main__":
    unittest.main()
