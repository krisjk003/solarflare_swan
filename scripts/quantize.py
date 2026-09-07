import sys
import os
import torch
import torch.nn as nn
import copy
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.custom_cnn1d import CustomCNN1D
from models.custom_cnn1d_int8 import CustomCNN1D_INT8, CustomCNN1D_INT7
from models.quantization import calculate_symmetric_scale, quantize_int8, quantize_bias_int32, compute_multiplier_shift
from data.dataset import _get_partition_files, load_files_to_matrix, create_dataloader
from data.preprocess import remove_mostly_bad, official_nan_to_num, transform_minmax, TargetExtractor

def fuse_conv_bn(conv, bn):
    fused_conv = nn.Conv1d(
        conv.in_channels, conv.out_channels, kernel_size=conv.kernel_size,
        stride=conv.stride, padding=conv.padding, dilation=conv.dilation,
        groups=conv.groups, bias=True, padding_mode=conv.padding_mode
    )
    
    w_conv = conv.weight.data.clone()
    b_conv = conv.bias.data.clone() if conv.bias is not None else torch.zeros(conv.out_channels)
    
    bn_running_mean = bn.running_mean
    bn_running_var = bn.running_var
    bn_gamma = bn.weight
    bn_beta = bn.bias
    bn_eps = bn.eps
    
    factor = bn_gamma / torch.sqrt(bn_running_var + bn_eps)
    fused_w = w_conv * factor.unsqueeze(-1).unsqueeze(-1)
    fused_b = (b_conv - bn_running_mean) * factor + bn_beta
    
    fused_conv.weight.data = fused_w
    fused_conv.bias.data = fused_b
    
    return fused_conv

def build_fused_fp32_model(fp32_model):
    model = copy.deepcopy(fp32_model)
    model.eval()
    
    model.b1_pw = fuse_conv_bn(model.b1_pw, model.b1_bn)
    model.b1_bn = nn.Identity()
    
    model.b2_pw = fuse_conv_bn(model.b2_pw, model.b2_bn)
    model.b2_bn = nn.Identity()
    
    model.b3_pw = fuse_conv_bn(model.b3_pw, model.b3_bn)
    model.b3_bn = nn.Identity()
    
    model.b4_pw = fuse_conv_bn(model.b4_pw, model.b4_bn)
    model.b4_bn = nn.Identity()
    
    return model

def prepare_calibration_data(data_dir, partitions_str, checkpoint_preprocessing, max_samples):
    partitions = [p.strip() for p in partitions_str.split(',')]
    
    # EXPLICIT P5 PROTECTION
    for p in partitions:
        if '5' in p:
            raise ValueError("CRITICAL ERROR: P5 is forbidden from calibration!")
            
    partition_dirs = [f"partition{p}" for p in partitions]
    
    print(f"Selecting calibration files from: {partition_dirs}")
    all_files, _ = _get_partition_files(data_dir, partition_dirs)
    
    if len(all_files) == 0:
        raise ValueError("No files found in specified partitions.")
        
    if max_samples is not None and max_samples < len(all_files):
        # Deterministic sampling
        rng = np.random.default_rng(seed=42)
        idx = rng.choice(len(all_files), max_samples, replace=False)
        all_files = all_files[idx]
        
    print(f"Loading {len(all_files)} raw calibration files into RAM...")
    X_calib = load_files_to_matrix(all_files)
    y_calib = np.array([TargetExtractor.extract_binary(f) for f in all_files])
    
    print("Removing mostly bad instances...")
    X_calib, good_mask = remove_mostly_bad(X_calib)
    y_calib = y_calib[good_mask]
    
    print("Applying preprocessing from frozen checkpoint...")
    fallback_mean = np.array(checkpoint_preprocessing['fallback_mean'])
    X_min = np.array(checkpoint_preprocessing.get('min_val', checkpoint_preprocessing.get('X_min')))
    X_max = np.array(checkpoint_preprocessing.get('max_val', checkpoint_preprocessing.get('X_max')))
    
    if fallback_mean is None or X_min is None or X_max is None:
        raise ValueError("Checkpoint is missing required preprocessing parameters!")
        
    # Same strategy as pipeline inference
    X_calib = official_nan_to_num(X_calib, fallback_mean=fallback_mean)
    X_calib = transform_minmax(X_calib, X_min, X_max)
    
    # We do not apply NDBSR (B and C exclusion) here since calibration ranges 
    # should reflect all data the model might see, but it's arguable. We keep all validly formatted data.
    
    print(f"Final calibration dataset size: {len(X_calib)}")
    calib_loader = create_dataloader(X_calib, y_calib, batch_size=64, shuffle=False)
    
    return calib_loader

def run_calibration(fused_model, dataloader, device):
    """
    Collects dynamic ranges using hooks.
    """
    fused_model.to(device)
    fused_model.eval()
    
    act_max = {}
    
    def hook_fn(name):
        def hook(module, input, output):
            if name not in act_max:
                act_max[name] = 0.0
            val = output.detach().abs().max().item()
            act_max[name] = max(act_max[name], val)
        return hook

    hooks = []
    # Register hooks for intermediate tensors
    hooks.append(fused_model.b1_dw.register_forward_hook(hook_fn("b1_dw")))
    hooks.append(fused_model.b1_pw.register_forward_hook(hook_fn("b1_pw")))
    hooks.append(fused_model.b1_relu.register_forward_hook(hook_fn("b1_relu")))
    
    hooks.append(fused_model.b2_dw.register_forward_hook(hook_fn("b2_dw")))
    hooks.append(fused_model.b2_pw.register_forward_hook(hook_fn("b2_pw")))
    hooks.append(fused_model.b2_relu.register_forward_hook(hook_fn("b2_relu")))
    
    hooks.append(fused_model.b3_dw.register_forward_hook(hook_fn("b3_dw")))
    hooks.append(fused_model.b3_pw.register_forward_hook(hook_fn("b3_pw")))
    hooks.append(fused_model.b3_relu.register_forward_hook(hook_fn("b3_relu")))
    
    hooks.append(fused_model.b4_dw.register_forward_hook(hook_fn("b4_dw")))
    hooks.append(fused_model.b4_pw.register_forward_hook(hook_fn("b4_pw")))
    hooks.append(fused_model.b4_relu.register_forward_hook(hook_fn("b4_relu")))
    
    # We also need input max
    act_max['input'] = 0.0
    
    with torch.no_grad():
        for x, _ in dataloader:
            x = x.to(device)
            act_max['input'] = max(act_max['input'], x.abs().max().item())
            
            # Forward pass manually to get mean and max pool ranges
            x = fused_model.b1_pool(fused_model.b1_relu(fused_model.b1_pw(fused_model.b1_dw(x))))
            x = fused_model.b2_pool(fused_model.b2_relu(fused_model.b2_pw(fused_model.b2_dw(x))))
            x = fused_model.b3_pool(fused_model.b3_relu(fused_model.b3_pw(fused_model.b3_dw(x))))
            x = fused_model.b4_relu(fused_model.b4_pw(fused_model.b4_dw(x)))
            
            x_mean = x.mean(dim=-1)
            x_max = x.max(dim=-1)[0]
            
            if 'x_mean' not in act_max: act_max['x_mean'] = 0.0
            if 'x_max' not in act_max: act_max['x_max'] = 0.0
            
            act_max['x_mean'] = max(act_max['x_mean'], x_mean.abs().max().item())
            act_max['x_max'] = max(act_max['x_max'], x_max.abs().max().item())
            
            x_concat = torch.cat([x_mean, x_max], dim=1)
            if 'x_concat' not in act_max: act_max['x_concat'] = 0.0
            act_max['x_concat'] = max(act_max['x_concat'], x_concat.abs().max().item())
            
            x = fused_model.classifier[0](x_concat)
            if 'fc1' not in act_max: act_max['fc1'] = 0.0
            act_max['fc1'] = max(act_max['fc1'], x.abs().max().item())
            
            x = fused_model.classifier[1](x)
            if 'fc1_relu' not in act_max: act_max['fc1_relu'] = 0.0
            act_max['fc1_relu'] = max(act_max['fc1_relu'], x.abs().max().item())
            
            x = fused_model.classifier[3](x)
            if 'fc2' not in act_max: act_max['fc2'] = 0.0
            act_max['fc2'] = max(act_max['fc2'], x.abs().max().item())
            
    for h in hooks:
        h.remove()
        
    return act_max

def quantize_layer(fp32_layer, int8_layer, in_scale, out_scale):
    w_scale = calculate_symmetric_scale(fp32_layer.weight.data)
    int8_layer.weight_scale.copy_(w_scale)
    int8_layer.input_scale.copy_(in_scale)
    int8_layer.output_scale.copy_(out_scale)
    
    int8_layer.weight_int8.copy_(quantize_int8(fp32_layer.weight.data, w_scale))
    
    acc_scale = in_scale * w_scale
    if hasattr(fp32_layer, 'bias') and fp32_layer.bias is not None and hasattr(int8_layer, 'bias_int32') and int8_layer.bias_int32 is not None:
        int8_layer.bias_int32.copy_(quantize_bias_int32(fp32_layer.bias.data, acc_scale))
        
    real_multiplier = acc_scale / out_scale
    m, s = compute_multiplier_shift(real_multiplier.item())
    int8_layer.multiplier.copy_(torch.tensor(m, dtype=torch.int32))
    int8_layer.shift.copy_(torch.tensor(s, dtype=torch.int32))

def convert_to_int8(fused_model, act_max):
    int8_model = CustomCNN1D_INT8()
    
    def get_scale(name):
        return torch.tensor(act_max[name] / 127.0).clamp(min=1e-8)
        
    in_scale = get_scale('input')
    int8_model.input_scale.copy_(in_scale)
    
    # Block 1
    quantize_layer(fused_model.b1_dw, int8_model.b1_dw, in_scale, get_scale('b1_dw'))
    quantize_layer(fused_model.b1_pw, int8_model.b1_pw, get_scale('b1_dw'), get_scale('b1_pw'))
    
    # Block 2 (Input is pool of b1_relu. MaxPool doesn't change scale, so input is b1_relu)
    quantize_layer(fused_model.b2_dw, int8_model.b2_dw, get_scale('b1_relu'), get_scale('b2_dw'))
    quantize_layer(fused_model.b2_pw, int8_model.b2_pw, get_scale('b2_dw'), get_scale('b2_pw'))
    
    # Block 3
    quantize_layer(fused_model.b3_dw, int8_model.b3_dw, get_scale('b2_relu'), get_scale('b3_dw'))
    quantize_layer(fused_model.b3_pw, int8_model.b3_pw, get_scale('b3_dw'), get_scale('b3_pw'))
    
    # Block 4
    quantize_layer(fused_model.b4_dw, int8_model.b4_dw, get_scale('b3_relu'), get_scale('b4_dw'))
    quantize_layer(fused_model.b4_pw, int8_model.b4_pw, get_scale('b4_dw'), get_scale('b4_pw'))
    
    # Mean Pool
    # Mean pool sum scale = b4_relu scale
    mean_in_scale = get_scale('b4_relu')
    mean_out_scale = get_scale('x_mean')
    # real multiplier for mean = mean_in_scale / (7 * mean_out_scale)
    m_mean, s_mean = compute_multiplier_shift((mean_in_scale / (7.0 * mean_out_scale)).item())
    int8_model.mean_pool.input_scale.copy_(mean_in_scale)
    int8_model.mean_pool.output_scale.copy_(mean_out_scale)
    int8_model.mean_pool.multiplier.copy_(torch.tensor(m_mean, dtype=torch.int32))
    int8_model.mean_pool.shift.copy_(torch.tensor(s_mean, dtype=torch.int32))
    
    # Max Pool alignment for Concat
    max_in_scale = get_scale('b4_relu')
    concat_scale = get_scale('x_concat') # we force mean and max to this scale
    # Requantize max pool output (which inherently has scale max_in_scale) to concat_scale
    m_max, s_max = compute_multiplier_shift((max_in_scale / concat_scale).item())
    int8_model.concat_max_multiplier.copy_(torch.tensor(m_max, dtype=torch.int32))
    int8_model.concat_max_shift.copy_(torch.tensor(s_max, dtype=torch.int32))
    
    # We must also force mean pool output scale to be exactly concat_scale to prevent issues
    m_mean, s_mean = compute_multiplier_shift((mean_in_scale / (7.0 * concat_scale)).item())
    int8_model.mean_pool.output_scale.copy_(concat_scale)
    int8_model.mean_pool.multiplier.copy_(torch.tensor(m_mean, dtype=torch.int32))
    int8_model.mean_pool.shift.copy_(torch.tensor(s_mean, dtype=torch.int32))
    
    # Classifier
    quantize_layer(fused_model.classifier[0], int8_model.fc1, concat_scale, get_scale('fc1'))
    quantize_layer(fused_model.classifier[3], int8_model.fc2, get_scale('fc1_relu'), get_scale('fc2'))
    
    return int8_model

# Backward compatibility alias
convert_to_int7 = convert_to_int8

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, default="checkpoints/custom_cnn1d_best_leakage_free.pt")
    # Calibration args enforcing P1-P3
    parser.add_argument("--calib_partitions", type=str, default="1,2,3", help="Comma-separated partition numbers. NEVER 5.")
    parser.add_argument("--data_dir", type=str, default="data/raw/SWAN-SF")
    parser.add_argument("--calibration_samples", type=int, default=1000, help="Number of files to sample for calibration.")
    args = parser.parse_args()
    
    # Ensure P5 cannot be used
    if "5" in args.calib_partitions.split(","):
        raise ValueError("CRITICAL ERROR: P5 is forbidden from calibration!")
        
    device = torch.device("cpu")
    print(f"Loading FP32 checkpoint from {args.checkpoint}")
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    
    fp32_model = CustomCNN1D(in_channels=24)
    fp32_model.load_state_dict(checkpoint['model_state_dict'])
    
    print("Fusing BatchNorms...")
    fused_model = build_fused_fp32_model(fp32_model)
    
    print("Preparing actual SWAN-SF calibration dataset...")
    calib_loader = prepare_calibration_data(
        data_dir=args.data_dir,
        partitions_str=args.calib_partitions,
        checkpoint_preprocessing=checkpoint['preprocessing'],
        max_samples=args.calibration_samples
    )
    
    print("Running static calibration with REAL SWAN-SF dataset...")
    act_max = run_calibration(fused_model, calib_loader, device)
    
    print("Converting to INT8 Fixed-Point Model...")
    int8_model = convert_to_int8(fused_model, act_max)
    
    out_dir = "checkpoints/int8"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "custom_cnn1d_int8.pt")
    
    torch.save({
        'model_state_dict': int8_model.state_dict(),
        'act_max_dict': act_max,
        'calib_partitions': args.calib_partitions,
        'calibration_samples': args.calibration_samples,
        'preprocessing': checkpoint.get('preprocessing', {})
    }, out_path)
    
    print(f"INT8 model saved to {out_path}")

if __name__ == "__main__":
    main()
