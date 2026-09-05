import torch
import torch.nn as nn
import torch.nn.functional as F

class Cmod(nn.Module):
    """
    Cmod Neural Network Architecture exactly reproduced from the official repository:
    https://github.com/foumani/solar_flare_cnn
    
    Expected input shape: [batch_size, 24, 60]
    Expected output shape: [batch_size, 1] (raw logits)
    """
    def __init__(self, in_channels=24):
        super(Cmod, self).__init__()
        
        # Hyperparameters from official config (optimal_model)
        kernel_sizes = [9, 9, 9]
        depths = [2, 4, 8]
        pooling_size = 2
        hidden = [128, 32]
        self.data_dropout_p = 0.0
        self.layer_dropout_p = 0.3
        
        # Block 1
        self.conv1 = nn.Conv1d(in_channels=in_channels,
                               out_channels=depths[0],
                               kernel_size=kernel_sizes[0],
                               padding=(kernel_sizes[0] - 1) // 2,
                               bias=True)
        self.batch_norm1 = nn.BatchNorm1d(depths[0])
        self.pool1 = nn.MaxPool1d(kernel_size=pooling_size, stride=2)
        
        # Block 2
        self.conv2 = nn.Conv1d(in_channels=depths[0],
                               out_channels=depths[1],
                               kernel_size=kernel_sizes[1],
                               padding=(kernel_sizes[1] - 1) // 2,
                               bias=True)
        self.batch_norm2 = nn.BatchNorm1d(depths[1])
        self.pool2 = nn.MaxPool1d(kernel_size=pooling_size, stride=2)
        
        # Block 3
        self.conv3 = nn.Conv1d(in_channels=depths[1],
                               out_channels=depths[2],
                               kernel_size=kernel_sizes[2],
                               padding=(kernel_sizes[2] - 1) // 2,
                               bias=True)
        self.batch_norm3 = nn.BatchNorm1d(depths[2])
        self.pool3 = nn.MaxPool1d(kernel_size=pooling_size, stride=2)
        
        # Fully Connected Layers
        # Using LazyLinear to match official implementation dynamically
        self.linear1 = nn.LazyLinear(out_features=hidden[0])
        self.linear2 = nn.Linear(in_features=hidden[0], out_features=hidden[1])
        
        # Output Layer (Binary logits for BCEWithLogitsLoss)
        self.l_out = nn.Linear(in_features=hidden[1], out_features=1)
        
        # Xavier initialization
        torch.nn.init.xavier_uniform_(self.conv1.weight)
        torch.nn.init.xavier_uniform_(self.conv2.weight)
        torch.nn.init.xavier_uniform_(self.conv3.weight)
        # Note: LazyLinear weights cannot be initialized before they are materialized by a forward pass.
        # But we initialize the ones we can.
        torch.nn.init.xavier_uniform_(self.linear2.weight)
        torch.nn.init.xavier_uniform_(self.l_out.weight)

    def forward(self, X):
        # Input dropout
        X = F.dropout(X, p=self.data_dropout_p, training=self.training)
        
        # Block 1
        X = self.conv1(X)
        X = self.batch_norm1(X)
        X = self.pool1(F.leaky_relu(X))
        X = F.dropout(X, p=self.layer_dropout_p, training=self.training)
        
        # Block 2
        X = self.conv2(X)
        X = self.batch_norm2(X)
        X = self.pool2(F.leaky_relu(X))
        X = F.dropout(X, p=self.layer_dropout_p, training=self.training)
        
        # Block 3
        X = self.conv3(X)
        X = self.batch_norm3(X)
        X = self.pool3(F.leaky_relu(X))
        X = F.dropout(X, p=self.layer_dropout_p, training=self.training)
        
        # Flatten
        X = X.reshape(X.shape[0], -1)
        
        # FC 1
        X = F.leaky_relu(self.linear1(X))
        X = F.dropout(X, p=self.layer_dropout_p, training=self.training)
        
        # FC 2
        X = F.leaky_relu(self.linear2(X))
        X = F.dropout(X, p=self.layer_dropout_p, training=self.training)
        
        # Output Logits
        X = self.l_out(X)
        
        return X

    def initialize_lazy_layers(self, dummy_input):
        """
        Helper method to run a dummy forward pass and then apply xavier init to LazyLinear.
        """
        _ = self.forward(dummy_input)
        torch.nn.init.xavier_uniform_(self.linear1.weight)
