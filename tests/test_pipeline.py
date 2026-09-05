import os
import unittest
import numpy as np
import torch
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.dataset import get_dataloaders
from data.preprocess import Preprocessor
from data.synthetic import generate_synthetic_partition
from models.quantization import FakeQuantize7Bit

class TestDataPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test config and synthetic data
        cls.config = {
            'data': {
                'features': 24,
                'sequence_length': 60,
                'prediction_window': 12,
                'partitions': [1, 2, 3],
                'train_partitions': [1],
                'val_partitions': [2],
                'test_partitions': [3],
                'missing_value_handling': 'forward_fill',
                'normalization': 'standard',
                'class_balancing': 'none'
            },
            'training': {
                'batch_size': 16
            }
        }
        cls.data_dir = "/tmp/swan_sf_test_data"
        os.makedirs(cls.data_dir, exist_ok=True)
        for i in range(1, 4):
            generate_synthetic_partition(i, num_samples=50, seq_len=60, num_features=24, output_dir=cls.data_dir)

    def test_missing_value_handling(self):
        # Create data with NaNs
        np.random.seed(0)
        X = np.random.randn(10, 60, 24)
        X[0, 5, 10] = np.nan # middle nan
        X[1, 0, 0] = np.nan  # start nan
        
        preprocessor = Preprocessor(self.config)
        X_clean = preprocessor._handle_missing(X)
        
        self.assertFalse(np.isnan(X_clean).any(), "Missing values were not handled correctly.")
        
    def test_normalization_and_leakage(self):
        # Test that preprocessor computes mean/std correctly on train, and applies same on val
        train_loader, val_loader, test_loader = get_dataloaders(self.config, self.data_dir)
        
        train_ds = train_loader.dataset
        val_ds = val_loader.dataset
        
        # Check that val dataset uses the train dataset's preprocessor
        self.assertEqual(train_ds.preprocessor, val_ds.preprocessor, "Validation set must use the same fitted preprocessor as the training set.")
        self.assertTrue(train_ds.preprocessor.is_fitted, "Preprocessor should be fitted.")
        
        # Check standard normalization properties on train set (mean ~ 0, std ~ 1)
        X_train_scaled = train_ds.X_scaled
        mean = np.mean(X_train_scaled)
        std = np.std(X_train_scaled)
        
        self.assertTrue(np.abs(mean) < 0.1, f"Mean should be close to 0, got {mean}")
        self.assertTrue(np.abs(std - 1.0) < 0.1, f"Std should be close to 1, got {std}")

    def test_tensor_shapes_and_labels(self):
        train_loader, _, _ = get_dataloaders(self.config, self.data_dir)
        for x, y in train_loader:
            # PyTorch Conv1d expects (batch_size, channels, length)
            self.assertEqual(x.shape, (16, 24, 60))
            self.assertEqual(y.shape, (16,))
            
            # Check labels are binary
            self.assertTrue(torch.all((y == 0) | (y == 1)), "Labels must be binary 0 or 1.")
            break
            
    def test_quantization_ranges(self):
        # Test 7-bit quantization logic
        quantizer = FakeQuantize7Bit(num_bits=7)
        quantizer.eval() # Must be in eval mode to trigger quantization
        
        # Input tensor with large range
        x = torch.linspace(-100, 100, steps=1000)
        x_dq = quantizer(x)
        
        # In symmetric fake quantization, the output values should have at most 128 unique levels (for 7-bit)
        # However, due to scale multiplication, the values are scaled back.
        # Let's check the underlying quantized values if we scale them back by the scale factor
        
        scale = 100 / 63 # max_abs / qmax
        x_q = torch.round(x_dq / scale)
        
        min_q = torch.min(x_q)
        max_q = torch.max(x_q)
        
        self.assertGreaterEqual(min_q.item(), -64, "Quantized value exceeded 7-bit minimum (-64)")
        self.assertLessEqual(max_q.item(), 63, "Quantized value exceeded 7-bit maximum (63)")
        
if __name__ == '__main__':
    unittest.main()
