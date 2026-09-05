import sys
import os
import numpy as np
import pandas as pd
import warnings

# We want to catch the warnings and see when they happen.
warnings.simplefilter('always', RuntimeWarning)

# Features from dataset.py
FEATURES = [
    'TOTUSJH', 'TOTBSQ', 'TOTPOT', 'TOTUSJZ', 'ABSNJZH', 'SAVNCPP', 'USFLUX', 'TOTFZ',
    'MEANPOT', 'EPSZ', 'MEANSHR', 'SHRGT45', 'MEANGAM', 'MEANGBT', 'MEANGBZ', 'MEANGBH',
    'MEANJZH', 'TOTFY', 'MEANJZD', 'MEANALP', 'TOTFX', 'EPSY', 'EPSX', 'R_VALUE'
]

def analyze_nans(file_path):
    print(f"\nAnalyzing {file_path}...")
    df = pd.read_csv(file_path, sep='\t', usecols=FEATURES)[FEATURES]
    X = df.values.astype(np.float32)
    # X is [60, 24]
    
    total_elements = X.size
    initial_nans = np.isnan(X).sum()
    print(f"Total elements: {total_elements}")
    print(f"Initial NaNs: {initial_nans} ({initial_nans/total_elements*100:.2f}%)")
    
    # Check max consecutive NaNs per feature
    for feat_idx in range(24):
        nans_feat = np.isnan(X[:, feat_idx])
        if nans_feat.any():
            # count consecutive
            import itertools
            max_consecutive = max((sum(1 for _ in g) for k, g in itertools.groupby(nans_feat) if k), default=0)
            if max_consecutive >= 7:
                print(f"  Feature {FEATURES[feat_idx]} has {max_consecutive} consecutive NaNs!")

    # Local Avg Imputation
    X_out = X.copy()
    X_out = np.expand_dims(X_out, axis=0) # [1, 60, 24]
    
    empty_slices = 0
    for i in range(60):
        start_idx = max(0, i - 3)
        end_idx = min(60, i + 4)
        temp = X_out[:, start_idx:end_idx, :]
        
        # Check if any feature window is completely NaN
        # temp is [1, window, 24]
        window_all_nan = np.isnan(temp).all(axis=1) # [1, 24]
        empty_slices += window_all_nan.sum()
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            temp_mean = np.nanmean(temp, axis=1)
            if len(w) > 0:
                pass # Warning caught
        
        mask = np.isnan(X_out[:, i, :])
        X_out[:, i, :] = np.where(mask, temp_mean, X_out[:, i, :])
    
    local_avg_nans = np.isnan(X_out).sum()
    print(f"Completely-NaN 7-step windows encountered: {empty_slices}")
    print(f"NaNs remaining after local_avg: {local_avg_nans}")
    
    # Fallback Imputation
    fallback_empty = False
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        fallback = np.nanmean(X_out, axis=(0, 1))
        if len(w) > 0:
            fallback_empty = True
            
    if fallback_empty:
         print(f"Fallback average calculation encountered empty slice! (A feature is entirely NaN for this instance)")
         
    X_out = np.where(np.isnan(X_out), fallback, X_out)
    final_nans = np.isnan(X_out).sum()
    print(f"NaNs remaining after fallback: {final_nans}")

if __name__ == '__main__':
    # Find a few files with lots of NaNs
    import glob
    files = glob.glob('/home/jyothish/solar-flare-swan-fpga/data/raw/SWAN-SF/partition1/partition1/*/*.csv')
    np.random.seed(42)
    np.random.shuffle(files)
    
    analyzed = 0
    for f in files:
        df = pd.read_csv(f, sep='\t', usecols=FEATURES)[FEATURES]
        if np.isnan(df.values).sum() > 500: # find a file with significant NaNs
            analyze_nans(f)
            analyzed += 1
        if analyzed >= 3:
            break
