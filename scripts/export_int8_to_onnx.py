import sys
import os
import torch
import torch.onnx

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.custom_cnn1d_int8 import CustomCNN1D_INT8

def main():
    checkpoint_path = "checkpoints/int8_real/custom_cnn1d_int8_real.pt"
    onnx_output_dir = "checkpoints/onnx"
    onnx_output_path = os.path.join(onnx_output_dir, "custom_cnn1d_int8.onnx")

    # 1. Load the exact INT8 model architecture
    # Note: Our project uses custom Integer layers, not Brevitas.
    model = CustomCNN1D_INT8(in_channels=24)
    
    # 2. Load the checkpoint weights
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}")
        
    print(f"Loading INT8 checkpoint from {checkpoint_path}...")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    
    # Extract the model_state_dict from the checkpoint wrapper
    model.load_state_dict(checkpoint['model_state_dict'])
    
    # 3. Put the model in evaluation mode
    model.eval()
    
    # 4. Create the appropriate dummy input with the correct shape
    # The preprocessed sequences have 24 channels and 60 time steps.
    # The INT8 forward pass expects quantized int8 inputs.
    dummy_input = torch.randint(-128, 127, (1, 24, 60), dtype=torch.int8)

    # 5. Export the INT8 model to ONNX
    os.makedirs(onnx_output_dir, exist_ok=True)
    print(f"Exporting model to ONNX at {onnx_output_path}...")
    
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_output_path,
        export_params=True,
        opset_version=14,  # Opset 14 has good support for integer operations
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'}, 
            'output': {0: 'batch_size'}
        }
    )
    
    print("ONNX export complete.")

if __name__ == "__main__":
    main()
