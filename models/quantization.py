import torch
import torch.nn as nn
import torch.nn.functional as F

def calculate_symmetric_scale(x, qmax=63):
    max_abs = torch.max(torch.abs(x)).clamp(min=1e-8)
    return max_abs / qmax

def quantize_int7(x, scale):
    q = torch.round(x / scale).clamp(-64, 63)
    return q.to(torch.int8) # Using int8 container for INT7 values

def dequantize_int7(x_q, scale):
    return x_q.to(torch.float32) * scale

def quantize_bias_int32(bias, bias_scale):
    q = torch.round(bias / bias_scale).clamp(-2147483648, 2147483647)
    return q.to(torch.int32)

def compute_multiplier_shift(real_multiplier, max_shift=31):
    """
    Approximates real_multiplier as (m / 2^s).
    """
    if real_multiplier == 0:
        return 0, 0
    
    # We want m to be a large integer for precision, typically fitting in 32-bit.
    # Let's find a shift such that real_multiplier * 2^shift < 2^31
    # Simple approach: shift = 31 - ceil(log2(real_multiplier)) (ignoring sign)
    import math
    if real_multiplier >= 1:
        s = 0
        while real_multiplier < (1 << (30 - s)) and s < max_shift:
            s += 1
        m = round(real_multiplier * (1 << s))
        return m, s
    else:
        # real_multiplier < 1
        s = 0
        while real_multiplier * (1 << s) < (1 << 30) and s < max_shift:
            s += 1
        m = round(real_multiplier * (1 << s))
        return m, s

def requantize(acc_int32, multiplier, shift):
    """
    Requantizes an INT32 accumulator to INT7.
    acc_int32: [B, C, L] or similar, INT32 tensor.
    multiplier: int
    shift: int
    """
    # Use torch.int64 to prevent overflow during multiplier application
    acc = acc_int32.to(torch.int64) * multiplier
    
    # Add rounding offset
    if shift > 0:
        rounding_offset = 1 << (shift - 1)
        acc = acc + rounding_offset
        acc = acc >> shift
        
    return acc.clamp(-64, 63).to(torch.int8)

class IntegerConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.groups = groups
        
        self.register_buffer('weight_int7', torch.zeros(out_channels, in_channels // groups, kernel_size, dtype=torch.int8))
        if bias:
            self.register_buffer('bias_int32', torch.zeros(out_channels, dtype=torch.int32))
        else:
            self.register_buffer('bias_int32', None)
            
        self.register_buffer('input_scale', torch.tensor(1.0))
        self.register_buffer('weight_scale', torch.tensor(1.0))
        self.register_buffer('output_scale', torch.tensor(1.0))
        self.register_buffer('multiplier', torch.tensor(0, dtype=torch.int32))
        self.register_buffer('shift', torch.tensor(0, dtype=torch.int32))
        
    def forward(self, x_int7):
        # x_int7: [B, C, L] int8 container with values in [-64, 63]
        B, C_in, L_in = x_int7.shape
        C_out = self.out_channels
        in_per_group = C_in // self.groups
        out_per_group = C_out // self.groups
        K = self.kernel_size
        
        L_out = (L_in + 2 * self.padding - self.dilation * (K - 1) - 1) // self.stride + 1
        
        x_32 = x_int7.to(torch.int32)
        if self.padding > 0:
            x_32 = F.pad(x_32, (self.padding, self.padding), mode='constant', value=0)
            
        w_32 = self.weight_int7.to(torch.int32)
        acc = torch.zeros((B, C_out, L_out), dtype=torch.int32, device=x_int7.device)
        
        for g in range(self.groups):
            x_g = x_32[:, g * in_per_group : (g + 1) * in_per_group, :]
            w_g = w_32[g * out_per_group : (g + 1) * out_per_group, :, :]
            
            for k in range(K):
                offset = k * self.dilation
                x_slice = x_g[:, :, offset : offset + L_out * self.stride : self.stride]
                w_k = w_g[:, :, k]
                # Integer matrix multiplication in int32: [B, in_per_group, L_out]^T @ w_k^T
                prod = torch.matmul(x_slice.transpose(1, 2), w_k.t()).transpose(1, 2)
                acc[:, g * out_per_group : (g + 1) * out_per_group, :] += prod
                
        if self.bias_int32 is not None:
            acc += self.bias_int32.view(1, C_out, 1)
            
        # Requantize int32 accumulator to int7
        out_int7 = requantize(acc, self.multiplier.item(), self.shift.item())
        return out_int7

class IntegerLinear(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        self.register_buffer('weight_int7', torch.zeros(out_features, in_features, dtype=torch.int8))
        if bias:
            self.register_buffer('bias_int32', torch.zeros(out_features, dtype=torch.int32))
        else:
            self.register_buffer('bias_int32', None)
            
        self.register_buffer('input_scale', torch.tensor(1.0))
        self.register_buffer('weight_scale', torch.tensor(1.0))
        self.register_buffer('output_scale', torch.tensor(1.0))
        self.register_buffer('multiplier', torch.tensor(0, dtype=torch.int32))
        self.register_buffer('shift', torch.tensor(0, dtype=torch.int32))
        
    def forward(self, x_int7):
        # x_int7: [B, in_features] in int8
        x_32 = x_int7.to(torch.int32)
        w_32 = self.weight_int7.to(torch.int32)
        # Integer matrix multiplication in int32
        acc = torch.matmul(x_32, w_32.t())
        if self.bias_int32 is not None:
            acc = acc + self.bias_int32.view(1, -1)
            
        out_int7 = requantize(acc, self.multiplier.item(), self.shift.item())
        return out_int7

class IntegerReLU(nn.Module):
    def forward(self, x_int7):
        return torch.clamp(x_int7, min=0)

class IntegerMaxPool1d(nn.Module):
    def __init__(self, kernel_size, stride=None, padding=0):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride if stride is not None else kernel_size
        self.padding = padding
        
    def forward(self, x_int7):
        # x_int7: [B, C, L] int8
        x = x_int7
        if self.padding > 0:
            x = F.pad(x, (self.padding, self.padding), mode='constant', value=-64)
        windows = x.unfold(2, self.kernel_size, self.stride)
        out = windows.max(dim=-1).values
        return out

class IntegerMeanPool(nn.Module):
    def __init__(self, window_size=7):
        super().__init__()
        self.window_size = window_size
        self.register_buffer('input_scale', torch.tensor(1.0))
        self.register_buffer('output_scale', torch.tensor(1.0))
        self.register_buffer('multiplier', torch.tensor(0, dtype=torch.int32))
        self.register_buffer('shift', torch.tensor(0, dtype=torch.int32))
        
    def forward(self, x_int7):
        # x_int7: [B, C, L]
        # Sum over L
        acc_int32 = x_int7.to(torch.int32).sum(dim=-1) # [B, C]
        
        # Requantize (handles division by window_size AND scale change)
        out_int7 = requantize(acc_int32, self.multiplier.item(), self.shift.item())
        return out_int7
