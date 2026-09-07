import sys
import os
import json
import torch
import torch.nn as nn

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.custom_cnn1d_int8 import CustomCNN1D_INT8, CustomCNN1D_INT7
from models.quantization import IntegerConv1d, IntegerLinear, IntegerMaxPool1d, IntegerMeanPool

def export_int_array(f, name, tensor, c_type="ap_int<8>"):
    flat = tensor.flatten().tolist()
    f.write(f"const {c_type} {name}[{len(flat)}] = {{\n  ")
    for i, val in enumerate(flat):
        f.write(f"{val}")
        if i != len(flat) - 1:
            f.write(", ")
        if (i + 1) % 16 == 0 and i != len(flat) - 1:
            f.write("\n  ")
    f.write("\n};\n\n")

def get_layer_metadata(name, layer, in_dims, out_dims, op_type=None):
    meta = {
        "layer_name": name,
        "operation_type": op_type or layer.__class__.__name__,
        "input_dimensions": in_dims,
        "output_dimensions": out_dims,
    }
    
    if isinstance(layer, IntegerConv1d):
        is_dw = layer.groups > 1
        meta.update({
            "operation_type": "DepthwiseConv1d" if is_dw else ("PointwiseConv1d" if layer.kernel_size == 1 else "Conv1d"),
            "input_channels": int(layer.in_channels),
            "output_channels": int(layer.out_channels),
            "kernel_size": int(layer.kernel_size),
            "stride": int(layer.stride),
            "padding": int(layer.padding),
            "dilation": int(layer.dilation),
            "groups": int(layer.groups),
            "input_scale": float(layer.input_scale.item()),
            "weight_scale": float(layer.weight_scale.item()),
            "output_scale": float(layer.output_scale.item()),
            "multiplier": int(layer.multiplier.item()),
            "shift": int(layer.shift.item()),
            "bias_info": {
                "has_bias": layer.bias_int32 is not None,
                "dtype": "ap_int<32>" if layer.bias_int32 is not None else None,
                "size": int(layer.bias_int32.numel()) if layer.bias_int32 is not None else 0
            }
        })
    elif isinstance(layer, IntegerLinear):
        meta.update({
            "operation_type": "Linear",
            "input_channels": int(layer.in_features),
            "output_channels": int(layer.out_features),
            "kernel_size": 1,
            "stride": 1,
            "padding": 0,
            "dilation": 1,
            "groups": 1,
            "input_scale": float(layer.input_scale.item()),
            "weight_scale": float(layer.weight_scale.item()),
            "output_scale": float(layer.output_scale.item()),
            "multiplier": int(layer.multiplier.item()),
            "shift": int(layer.shift.item()),
            "bias_info": {
                "has_bias": layer.bias_int32 is not None,
                "dtype": "ap_int<32>" if layer.bias_int32 is not None else None,
                "size": int(layer.bias_int32.numel()) if layer.bias_int32 is not None else 0
            }
        })
    elif isinstance(layer, IntegerMaxPool1d):
        meta.update({
            "operation_type": "MaxPool1d",
            "input_channels": int(in_dims[0]),
            "output_channels": int(out_dims[0]),
            "kernel_size": int(layer.kernel_size),
            "stride": int(layer.stride),
            "padding": int(layer.padding),
            "dilation": 1,
            "groups": int(in_dims[0]),
            "bias_info": {"has_bias": False, "size": 0}
        })
    elif isinstance(layer, IntegerMeanPool):
        meta.update({
            "operation_type": "GlobalMeanPool",
            "input_channels": int(in_dims[0]),
            "output_channels": int(out_dims[0]),
            "kernel_size": int(layer.window_size),
            "stride": int(layer.window_size),
            "padding": 0,
            "dilation": 1,
            "groups": int(in_dims[0]),
            "input_scale": float(layer.input_scale.item()),
            "output_scale": float(layer.output_scale.item()),
            "multiplier": int(layer.multiplier.item()),
            "shift": int(layer.shift.item()),
            "bias_info": {"has_bias": False, "size": 0}
        })
    return meta

def export_hls_from_model(model, out_dir="results/hls_export"):
    os.makedirs(out_dir, exist_ok=True)
    header_path = os.path.join(out_dir, "weights.h")
    json_path = os.path.join(out_dir, "model_metadata.json")
    
    # Topology definition with explicit dimensions
    topology = [
        ("b1_dw", model.b1_dw, [24, 60], [24, 60], None),
        ("b1_pw", model.b1_pw, [24, 60], [24, 60], None),
        ("b1_relu", model.b1_relu, [24, 60], [24, 60], "ReLU"),
        ("b1_pool", model.b1_pool, [24, 60], [24, 30], None),
        
        ("b2_dw", model.b2_dw, [24, 30], [24, 30], None),
        ("b2_pw", model.b2_pw, [24, 30], [32, 30], None),
        ("b2_relu", model.b2_relu, [32, 30], [32, 30], "ReLU"),
        ("b2_pool", model.b2_pool, [32, 30], [32, 15], None),
        
        ("b3_dw", model.b3_dw, [32, 15], [32, 15], None),
        ("b3_pw", model.b3_pw, [32, 15], [64, 15], None),
        ("b3_relu", model.b3_relu, [64, 15], [64, 15], "ReLU"),
        ("b3_pool", model.b3_pool, [64, 15], [64, 7], None),
        
        ("b4_dw", model.b4_dw, [64, 7], [64, 7], None),
        ("b4_pw", model.b4_pw, [64, 7], [128, 7], None),
        ("b4_relu", model.b4_relu, [128, 7], [128, 7], "ReLU"),
        
        ("mean_pool", model.mean_pool, [128, 7], [128], None),
    ]
    
    layers_meta = []
    for name, mod, in_d, out_d, op_t in topology:
        layers_meta.append(get_layer_metadata(name, mod, in_d, out_d, op_t))
        
    # Global Max Pool metadata
    layers_meta.append({
        "layer_name": "global_max_pool",
        "operation_type": "GlobalMaxPool",
        "input_dimensions": [128, 7],
        "output_dimensions": [128],
        "input_channels": 128,
        "output_channels": 128,
        "kernel_size": 7,
        "stride": 7,
        "padding": 0,
        "dilation": 1,
        "groups": 128,
        "multiplier": int(model.concat_max_multiplier.item()),
        "shift": int(model.concat_max_shift.item()),
        "bias_info": {"has_bias": False, "size": 0}
    })
    
    # Concat metadata
    layers_meta.append({
        "layer_name": "concat_mean_max",
        "operation_type": "Concatenate",
        "input_dimensions": [[128], [128]],
        "output_dimensions": [256],
        "input_channels": 256,
        "output_channels": 256
    })
    
    # Classifier metadata
    layers_meta.append(get_layer_metadata("fc1", model.fc1, [256], [32]))
    layers_meta.append(get_layer_metadata("fc1_relu", model.fc1_relu, [32], [32], "ReLU"))
    layers_meta.append(get_layer_metadata("fc2", model.fc2, [32], [1]))
    
    metadata = {
        "model_name": "CustomCNN1D_INT8",
        "target": "Vivado HLS",
        "numerical_format": {
            "weight_bits": 8,
            "activation_bits": 8,
            "bias_bits": 32,
            "accumulator_bits": 32,
            "signed": True,
            "qmin": -128,
            "qmax": 127,
            "zero_point": 0
        },
        "input_dimensions": [24, 60],
        "input_scale": float(model.input_scale.item()),
        "layers": layers_meta
    }
    
    with open(json_path, "w") as jf:
        json.dump(metadata, jf, indent=2)
        
    with open(header_path, "w") as f:
        f.write("#pragma once\n")
        f.write("#include <ap_int.h>\n")
        f.write("#include <stdint.h>\n\n")
        
        f.write("// ==========================================================================\n")
        f.write("// CustomCNN1D INT8 Model Parameters & Topology Configuration for Vivado HLS\n")
        f.write("// ==========================================================================\n\n")
        
        f.write(f"#define MODEL_INPUT_CHANNELS 24\n")
        f.write(f"#define MODEL_INPUT_LENGTH 60\n")
        f.write(f"#define MODEL_INPUT_SCALE {model.input_scale.item():.8e}f\n\n")
        
        for meta in layers_meta:
            name_upper = meta["layer_name"].upper()
            f.write(f"// --- {meta['layer_name']} ({meta['operation_type']}) ---\n")
            if "input_channels" in meta:
                f.write(f"#define {name_upper}_IN_CHANNELS {meta['input_channels']}\n")
                f.write(f"#define {name_upper}_OUT_CHANNELS {meta['output_channels']}\n")
            if "kernel_size" in meta:
                f.write(f"#define {name_upper}_KERNEL_SIZE {meta['kernel_size']}\n")
                f.write(f"#define {name_upper}_STRIDE {meta['stride']}\n")
                f.write(f"#define {name_upper}_PADDING {meta['padding']}\n")
                f.write(f"#define {name_upper}_DILATION {meta['dilation']}\n")
                f.write(f"#define {name_upper}_GROUPS {meta['groups']}\n")
            if "multiplier" in meta:
                f.write(f"#define {name_upper}_MULTIPLIER {meta['multiplier']}\n")
                f.write(f"#define {name_upper}_SHIFT {meta['shift']}\n")
            if "input_scale" in meta:
                f.write(f"#define {name_upper}_INPUT_SCALE {meta['input_scale']:.8e}f\n")
                f.write(f"#define {name_upper}_WEIGHT_SCALE {meta.get('weight_scale', 1.0):.8e}f\n")
                f.write(f"#define {name_upper}_OUTPUT_SCALE {meta['output_scale']:.8e}f\n")
            f.write("\n")
            
        # Export weight & bias arrays
        f.write("// --- Weights & Biases Arrays ---\n\n")
        for name in ["b1_dw", "b1_pw", "b2_dw", "b2_pw", "b3_dw", "b3_pw", "b4_dw", "b4_pw", "fc1", "fc2"]:
            layer = getattr(model, name)
            export_int_array(f, f"{name}_weight", layer.weight_int8, "ap_int<8>")
            if layer.bias_int32 is not None:
                export_int_array(f, f"{name}_bias", layer.bias_int32, "ap_int<32>")
                
    print(f"HLS C++ header exported to {header_path}")
    print(f"HLS metadata JSON exported to {json_path}")
    return header_path, json_path

def main():
    checkpoint_path = "checkpoints/int8/custom_cnn1d_int8.pt"
    if not os.path.exists(checkpoint_path):
        # Fallback to int7 path if int8 checkpoint does not exist yet
        checkpoint_path = "checkpoints/int7/custom_cnn1d_int7.pt"
        if not os.path.exists(checkpoint_path):
            print(f"Skipping export: checkpoint not found.")
            return
        
    model = CustomCNN1D_INT8()
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    export_hls_from_model(model)

if __name__ == "__main__":
    main()
