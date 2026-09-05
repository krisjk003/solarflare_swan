import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.dataset import load_files_to_matrix, _get_partition_files
from data.preprocess import remove_mostly_bad, official_nan_to_num, fit_minmax, transform_minmax
from data.dataset import prepare_data

def test_pipeline():
    print("--- Diagnostics on Data Pipeline ---")
    data_dir = "/home/jyothish/solar-flare-swan-fpga/data/raw/SWAN-SF"
    
    # 1. Manually test a small chunk to count NaNs
    print("Loading 20 raw instances...")
    files, _ = _get_partition_files(data_dir, ['partition1'])
    np.random.seed(42)
    files = np.random.choice(files, 20, replace=False)
    
    X = load_files_to_matrix(files)
    
    nans_initial = np.isnan(X).sum()
    print(f"Raw instances: {len(X)}")
    
    X_good, good_mask = remove_mostly_bad(X)
    print(f"Removed due to >25% missing: {len(X) - len(X_good)}")
    print(f"Remaining instances: {len(X_good)}")
    
    nans_before_impute = np.isnan(X_good).sum()
    print(f"NaNs before local_avg: {nans_before_impute}")
    
    # Check intermediate local_avg output
    import warnings
    X_temp = X_good.copy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for i in range(60):
            temp = X_temp[:, :, max(0, i - 3):min(60, i + 4)]
            temp = np.nanmean(temp, axis=2)
            X_temp[:, :, i] = np.where(np.isnan(X_temp[:, :, i]), temp, X_temp[:, :, i])
    print(f"NaNs after local_avg: {np.isnan(X_temp).sum()}")
    
    # Run official nan_to_num (includes local_avg and fallback)
    X_imputed = official_nan_to_num(X_good)
    nans_after = np.isnan(X_imputed).sum()
    print(f"NaNs after fallback: {nans_after}")
    assert nans_after == 0, "There are still NaNs after fallback!"
    
    print("\n--- Testing Full prepare_data Flow (Subset) ---")
    # 2. Run full prepare_data on a tiny subset
    train_loader, val_loader, test_loader, config = prepare_data(
        data_dir, batch_size=4, num_workers=0, max_files=100, test_max_files=20
    )
    
    print("\n--- Final Shapes ---")
    print(f"Train shape: {len(train_loader.dataset)}")
    print(f"Validation shape: {len(val_loader.dataset)}")
    print(f"Test shape: {len(test_loader.dataset)}")
    x_min = np.array(config['X_min'])
    print(f"Normalization min/max shapes: {x_min.shape}")
    
if __name__ == "__main__":
    test_pipeline()
