import torch
import torch.nn as nn

class CustomCNN1D(nn.Module):
    def __init__(self, in_channels=24):
        super(CustomCNN1D, self).__init__()
        
        # BLOCK 1
        self.b1_dw = nn.Conv1d(in_channels, in_channels, kernel_size=3, padding=1, groups=in_channels)
        self.b1_pw = nn.Conv1d(in_channels, 24, kernel_size=1)
        self.b1_bn = nn.BatchNorm1d(24)
        self.b1_relu = nn.ReLU()
        self.b1_pool = nn.MaxPool1d(kernel_size=2)
        
        # BLOCK 2
        self.b2_dw = nn.Conv1d(24, 24, kernel_size=3, padding=1, groups=24)
        self.b2_pw = nn.Conv1d(24, 32, kernel_size=1)
        self.b2_bn = nn.BatchNorm1d(32)
        self.b2_relu = nn.ReLU()
        self.b2_pool = nn.MaxPool1d(kernel_size=2)
        
        # BLOCK 3
        self.b3_dw = nn.Conv1d(32, 32, kernel_size=3, padding=1, groups=32)
        self.b3_pw = nn.Conv1d(32, 64, kernel_size=1)
        self.b3_bn = nn.BatchNorm1d(64)
        self.b3_relu = nn.ReLU()
        self.b3_pool = nn.MaxPool1d(kernel_size=2)
        
        # BLOCK 4
        self.b4_dw = nn.Conv1d(64, 64, kernel_size=3, padding=1, groups=64)
        self.b4_pw = nn.Conv1d(64, 128, kernel_size=1)
        self.b4_bn = nn.BatchNorm1d(128)
        self.b4_relu = nn.ReLU()
        
        # CLASSIFIER
        self.dropout = nn.Dropout(0.25)
        self.classifier = nn.Linear(128, 1)
        
    def forward(self, x):
        # x shape: [B, 24, 60]
        
        # Block 1
        x = self.b1_pool(self.b1_relu(self.b1_bn(self.b1_pw(self.b1_dw(x))))) # [B, 24, 30]
        
        # Block 2
        x = self.b2_pool(self.b2_relu(self.b2_bn(self.b2_pw(self.b2_dw(x))))) # [B, 32, 15]
        
        # Block 3
        x = self.b3_pool(self.b3_relu(self.b3_bn(self.b3_pw(self.b3_dw(x))))) # [B, 64, 7]
        
        # Block 4
        x = self.b4_relu(self.b4_bn(self.b4_pw(self.b4_dw(x)))) # [B, 128, 7]
        
        # GAP
        x = x.mean(dim=-1) # [B, 128]
        
        # Classifier
        x = self.dropout(x)
        x = self.classifier(x) # [B, 1]
        
        return x
