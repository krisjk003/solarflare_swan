import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
import torch.nn as nn
from models.custom_cnn1d import CustomCNN1D

def main():
    print("--- CustomCNN1D Architecture Inspection ---")
    model = CustomCNN1D(in_channels=24)
    
    # 4. Dummy input
    x = torch.randn(4, 24, 60)
    
    # 2. Print architecture
    print("\nArchitecture:")
    print(model)
    
    # 3. Count trainable parameters
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nTotal Trainable Parameters: {total_params}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")
    
    model.to(device)
    x = x.to(device)
    
    # 5. Run forward pass
    out = model(x)
    
    # 6. Verify output shape
    print(f"\nInput shape: {x.shape}")
    print(f"Output shape: {out.shape}")
    assert out.shape == (4, 1), f"Expected output shape (4, 1), got {out.shape}"
    
    # 7. Verify finite values
    assert torch.isfinite(out).all(), "Output contains non-finite values!"
    
    # 8. Dummy BCEWithLogitsLoss
    dummy_target = torch.empty(4, 1, dtype=torch.float).random_(2).to(device)
    criterion = nn.BCEWithLogitsLoss()
    loss = criterion(out, dummy_target)
    
    # 9. Backward pass
    loss.backward()
    
    print("\nForward and backward passes completed successfully!")

if __name__ == "__main__":
    main()
