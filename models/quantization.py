import torch
import torch.nn as nn

class FakeQuantize7Bit(nn.Module):
    """
    Simulates signed 7-bit quantization for FPGA compatibility.
    INT7 range: [-64, 63] for signed 7-bit two's complement.
    This module performs symmetric quantization.
    """
    def __init__(self, num_bits=7):
        super().__init__()
        self.num_bits = num_bits
        self.qmin = -(2 ** (num_bits - 1))
        self.qmax = (2 ** (num_bits - 1)) - 1
        
    def forward(self, x):
        if not self.training:
            # Calculate scale factor for symmetric quantization
            max_abs_val = torch.max(torch.abs(x))
            # Avoid division by zero
            max_abs_val = torch.clamp(max_abs_val, min=1e-8)
            
            scale = max_abs_val / self.qmax
            
            # Quantize
            x_q = torch.round(x / scale)
            
            # Clamp to INT7 range
            x_q = torch.clamp(x_q, self.qmin, self.qmax)
            
            # Dequantize (Fake quantization for PyTorch simulation)
            x_dq = x_q * scale
            
            # Custom gradient for rounding operation (Straight-Through Estimator)
            # but since we only use this in evaluation for now or QAT later,
            # simple fake quantization is sufficient.
            return (x_dq - x).detach() + x
        return x

class QuantizedConv1d(nn.Conv1d):
    """
    A 1D Convolutional layer that applies fake 7-bit quantization
    to its weights and activations to simulate FPGA inference.
    """
    def __init__(self, *args, **kwargs):
        num_bits = kwargs.pop('num_bits', 7)
        super().__init__(*args, **kwargs)
        self.weight_quantizer = FakeQuantize7Bit(num_bits=num_bits)
        self.act_quantizer = FakeQuantize7Bit(num_bits=num_bits)
        
    def forward(self, x):
        # Quantize activations
        x_q = self.act_quantizer(x)
        # Quantize weights
        weight_q = self.weight_quantizer(self.weight)
        
        return nn.functional.conv1d(
            x_q, weight_q, self.bias, self.stride, self.padding, self.dilation, self.groups
        )
