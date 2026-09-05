import numpy as np
import numpy.ma as ma
import os
import pandas as pd

FEATURES = [
    'TOTUSJH', 'TOTBSQ', 'TOTPOT', 'TOTUSJZ', 'ABSNJZH', 'SAVNCPP', 'USFLUX', 'TOTFZ',
    'MEANPOT', 'EPSZ', 'MEANSHR', 'SHRGT45', 'MEANGAM', 'MEANGBT', 'MEANGBZ', 'MEANGBH',
    'MEANJZH', 'TOTFY', 'MEANJZD', 'MEANALP', 'TOTFX', 'EPSY', 'EPSX', 'R_VALUE'
]

class TargetExtractor:
    @staticmethod
    def extract_class(file_path):
        basename = os.path.basename(file_path)
        return basename[0] if basename[0] != "F" else "Q"
        
    @staticmethod
    def extract_binary(file_path):
        flare_class = TargetExtractor.extract_class(file_path)
        return 0.0 if flare_class in ["Q", "B", "C"] else 1.0


def remove_mostly_bad(X, files_list=None):
    """
    Official remove_mostly_bad behavior:
    1. First 23 features treat 0 as np.nan
    2. Instances with >= 25% missing/zero values are removed
    X expected shape: [N, 24, 60]
    """
    if len(X) == 0:
        return X, np.array([], dtype=bool)
        
    X_out = X.copy()
    
    # First 23 features treat 0 as NaN
    mask_zero = (X_out[:, :23, :] == 0)
    X_out[:, :23, :][mask_zero] = np.nan
    
    is_nan_or_zero = (X_out == 0) | np.isnan(X_out)
    count_zero_or_nan = is_nan_or_zero.sum(axis=(1, 2))
    is_mostly_good = count_zero_or_nan < (60 * 24 / 8)
    
    return X_out[is_mostly_good], is_mostly_good


def official_nan_to_num(X, fallback_mean=None):
    """
    Official local_avg + avg fallback behavior.
    X expected shape: [N, 24, 60]
    """
    X_out = X.copy()
    if len(X_out) == 0:
        if fallback_mean is None:
            return X_out, None
        return X_out
        
    # Local Average Imputation (window=7)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for i in range(60):
            temp = X_out[:, :, max(0, i - 3):min(60, i + 4)]
            temp = np.nanmean(temp, axis=2)
            X_out[:, :, i] = np.where(np.isnan(X_out[:, :, i]), temp, X_out[:, :, i])

    # Global Fallback Imputation (avg)
    if fallback_mean is None:
        computed_fallback = ma.array(X_out, mask=np.isnan(X_out)).mean(axis=(0, 2))[:, np.newaxis]
        X_out = np.where(np.isnan(X_out), computed_fallback, X_out)
        return X_out, computed_fallback
    else:
        X_out = np.where(np.isnan(X_out), fallback_mean, X_out)
        return X_out


def fit_minmax(X):
    """ X shape: [N, 24, 60] """
    X_min = np.min(X, axis=(0, 2))[:, None]
    X_max = np.max(X, axis=(0, 2))[:, None]
    return X_min, X_max


def transform_minmax(X, X_min, X_max):
    X_out = (X - X_min) / (X_max - X_min + 1e-8)
    return X_out
