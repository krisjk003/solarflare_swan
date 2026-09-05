import os
import pickle
import numpy as np

def generate_synthetic_partition(partition_id, num_samples, seq_len, num_features, output_dir):
    """
    Generates synthetic SWAN-SF like data for a given partition.
    Introduces some artificial NaN values to test missing value handling.
    """
    np.random.seed(42 + partition_id)
    
    # Generate random features
    X = np.random.randn(num_samples, seq_len, num_features).astype(np.float32)
    
    # Introduce some NaNs randomly (e.g., 5% of data)
    mask = np.random.rand(*X.shape) < 0.05
    X[mask] = np.nan
    
    # Generate random binary labels (highly imbalanced)
    y = (np.random.rand(num_samples) > 0.9).astype(np.int64)
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"Partition{partition_id}.pkl")
    
    with open(filepath, 'wb') as f:
        pickle.dump({'X': X, 'y': y}, f)
        
    print(f"Generated {filepath} with shape {X.shape}")

def main():
    output_dir = "/home/jyothish/solar-flare-swan-fpga/data/synthetic"
    # Generate partitions 1 to 5
    for i in range(1, 6):
        generate_synthetic_partition(i, num_samples=100, seq_len=60, num_features=24, output_dir=output_dir)

if __name__ == "__main__":
    main()
