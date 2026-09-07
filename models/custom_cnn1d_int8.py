import torch
import torch.nn as nn
from models.quantization import IntegerConv1d, IntegerLinear, IntegerReLU, IntegerMaxPool1d, IntegerMeanPool, requantize

class CustomCNN1D_INT8(nn.Module):
    def __init__(self, in_channels=24):
        super().__init__()
        
        # BLOCK 1
        self.b1_dw = IntegerConv1d(in_channels, in_channels, kernel_size=3, padding=1, groups=in_channels, bias=False)
        self.b1_pw = IntegerConv1d(in_channels, 24, kernel_size=1, bias=True)
        self.b1_relu = IntegerReLU()
        self.b1_pool = IntegerMaxPool1d(kernel_size=2)
        
        # BLOCK 2
        self.b2_dw = IntegerConv1d(24, 24, kernel_size=3, padding=1, groups=24, bias=False)
        self.b2_pw = IntegerConv1d(24, 32, kernel_size=1, bias=True)
        self.b2_relu = IntegerReLU()
        self.b2_pool = IntegerMaxPool1d(kernel_size=2)
        
        # BLOCK 3
        self.b3_dw = IntegerConv1d(32, 32, kernel_size=3, padding=1, groups=32, bias=False)
        self.b3_pw = IntegerConv1d(32, 64, kernel_size=1, bias=True)
        self.b3_relu = IntegerReLU()
        self.b3_pool = IntegerMaxPool1d(kernel_size=2)
        
        # BLOCK 4
        self.b4_dw = IntegerConv1d(64, 64, kernel_size=3, padding=1, groups=64, bias=False)
        self.b4_pw = IntegerConv1d(64, 128, kernel_size=1, bias=True)
        self.b4_relu = IntegerReLU()
        
        # Global Pooling
        self.mean_pool = IntegerMeanPool(window_size=7)
        # Global max pool is just MaxPool over dim -1
        
        # Concat scaling alignment
        self.register_buffer('concat_max_multiplier', torch.tensor(0, dtype=torch.int32))
        self.register_buffer('concat_max_shift', torch.tensor(0, dtype=torch.int32))
        
        # CLASSIFIER
        self.fc1 = IntegerLinear(256, 32, bias=True)
        self.fc1_relu = IntegerReLU()
        self.fc2 = IntegerLinear(32, 1, bias=True)
        
        # Input quantization metadata
        self.register_buffer('input_scale', torch.tensor(1.0))
        
    def forward(self, x_int8):
        # x_int8: [B, 24, 60] INT8
        
        # Block 1
        x = self.b1_dw(x_int8)
        x = self.b1_pw(x)
        x = self.b1_relu(x)
        x = self.b1_pool(x)
        
        # Block 2
        x = self.b2_dw(x)
        x = self.b2_pw(x)
        x = self.b2_relu(x)
        x = self.b2_pool(x)
        
        # Block 3
        x = self.b3_dw(x)
        x = self.b3_pw(x)
        x = self.b3_relu(x)
        x = self.b3_pool(x)
        
        # Block 4
        x = self.b4_dw(x)
        x = self.b4_pw(x)
        x = self.b4_relu(x)
        
        # Mean + Max
        x_mean = self.mean_pool(x) # [B, 128] already requantized to target concat scale
        
        x_max_int32 = x.to(torch.int32).max(dim=-1).values
        # Requantize max vector to match the mean vector's scale for safe concatenation
        x_max = requantize(x_max_int32, self.concat_max_multiplier.item(), self.concat_max_shift.item())
        
        # Concat
        x_concat = torch.cat([x_mean, x_max], dim=1) # [B, 256] INT8
        
        # Classifier
        x = self.fc1(x_concat)
        x = self.fc1_relu(x)
        x = self.fc2(x)
        
        return x

# Backward compatibility alias
CustomCNN1D_INT7 = CustomCNN1D_INT8
