import os
import glob
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

from data.preprocess import TargetExtractor, remove_mostly_bad, official_nan_to_num, fit_minmax, transform_minmax, FEATURES

def _get_partition_files(data_dir, partitions):
    all_files = []
    classes = []
    for partition in partitions:
        partition_path = os.path.join(data_dir, partition, partition)
        for class_dir in ["FL", "NF"]:
            class_path = os.path.join(partition_path, class_dir)
            if not os.path.exists(class_path):
                continue
            files = glob.glob(os.path.join(class_path, "*.csv"))
            for f in files:
                all_files.append(f)
                classes.append(TargetExtractor.extract_class(f))
    return np.array(all_files), np.array(classes)


def load_files_to_matrix(files):
    """ Loads list of CSV files into an [N, 24, 60] numpy matrix """
    N = len(files)
    if N == 0:
        return np.empty((0, 24, 60), dtype=np.float32)
        
    X = np.empty((N, 24, 60), dtype=np.float32)
    for i, f in enumerate(files):
        df = pd.read_csv(f, sep='\t', usecols=FEATURES)
        # Reorder columns explicitly to match FEATURES order
        df = df[FEATURES]
        # Transpose to get [24, 60]
        X[i] = df.values.T
    return X


def create_dataloader(X, y, batch_size=64, shuffle=True, num_workers=4):
    dataset = FlairDataset(X, y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)


class FlairDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        
    def __len__(self):
        return len(self.X)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def prepare_data(data_dir, batch_size=64, num_workers=4, max_files=None, test_max_files=None):
    train_partitions = ['partition1', 'partition2', 'partition3', 'partition4']
    test_partitions = ['partition5']
    
    # 1. Load/select instances
    print("Selecting training files...")
    all_t_files, all_t_classes = _get_partition_files(data_dir, train_partitions)
    
    if max_files is not None:
        idx = np.random.choice(len(all_t_files), max_files, replace=False)
        all_t_files = all_t_files[idx]
        all_t_classes = all_t_classes[idx]
        
    # Official Sampling behavior (6500 neg, 1000 pos)
    rng = np.random.default_rng(seed=42)
    pos_mask = np.isin(all_t_classes, ['M', 'X'])
    neg_mask = np.isin(all_t_classes, ['Q', 'B', 'C'])
    
    pos_files = all_t_files[pos_mask]
    neg_files = all_t_files[neg_mask]
    
    n_neg = min(6500, len(neg_files)) if max_files is None else len(neg_files)
    n_pos = min(1000, len(pos_files)) if max_files is None else len(pos_files)
    
    sampled_neg = rng.choice(neg_files, n_neg, replace=False)
    sampled_pos = rng.choice(pos_files, n_pos, replace=False)
    
    selected_files = np.concatenate([sampled_neg, sampled_pos])
    rng.shuffle(selected_files) # Shuffle them together
    
    print(f"Loading {len(selected_files)} raw training files into RAM...")
    X_train_full = load_files_to_matrix(selected_files)
    y_train_full = np.array([TargetExtractor.extract_binary(f) for f in selected_files])
    
    print("Removing mostly bad instances from full training set...")
    n_before = len(X_train_full)
    X_train_full, good_mask = remove_mostly_bad(X_train_full)
    y_train_full = y_train_full[good_mask]
    selected_files = selected_files[good_mask]
    print(f"Removed {n_before - len(X_train_full)} instances due to >25% missing.")
    
    # 2. Create training/validation split
    print("Creating validation split...")
    val_p = 0.5
    n_total = len(X_train_full)
    val_idx = rng.choice(n_total, int(n_total * val_p), replace=False)
    train_mask = np.ones(n_total, dtype=bool)
    train_mask[val_idx] = False
    
    X_train, y_train, files_train = X_train_full[train_mask], y_train_full[train_mask], selected_files[train_mask]
    X_val, y_val = X_train_full[val_idx], y_train_full[val_idx]
    
    # 3. Apply nan_to_num to train and val separately
    print("Applying official_nan_to_num to train...")
    X_train = official_nan_to_num(X_train)
    print("Applying official_nan_to_num to val...")
    X_val = official_nan_to_num(X_val)
    
    # 4. Load P5 test set
    print("Selecting test files...")
    test_files, _ = _get_partition_files(data_dir, test_partitions)
    if test_max_files is not None:
        idx = np.random.choice(len(test_files), test_max_files, replace=False)
        test_files = test_files[idx]
        
    print(f"Loading {len(test_files)} test files into RAM...")
    X_test = load_files_to_matrix(test_files)
    y_test = np.array([TargetExtractor.extract_binary(f) for f in test_files])
    
    print("Removing mostly bad instances from test set...")
    X_test, good_mask = remove_mostly_bad(X_test)
    y_test = y_test[good_mask]
    
    # 5. Apply nan_to_num to P5
    print("Applying official_nan_to_num to test...")
    X_test = official_nan_to_num(X_test)
    
    # 6. Fit Min-Max normalizer on TRAIN ONLY
    print("Fitting Min-Max normalizer on train...")
    X_min, X_max = fit_minmax(X_train)
    X_train = transform_minmax(X_train, X_min, X_max)
    
    # 7 & 8. Transform validation and P5
    print("Transforming val and test...")
    X_val = transform_minmax(X_val, X_min, X_max)
    X_test = transform_minmax(X_test, X_min, X_max)
    
    # 9. Apply NDBSR to training data
    print("Applying NDBSR to train...")
    train_classes = np.array([TargetExtractor.extract_class(f) for f in files_train])
    ndbsr_mask = ~np.isin(train_classes, ['B', 'C'])
    X_train = X_train[ndbsr_mask]
    y_train = y_train[ndbsr_mask]
    
    print("Data preparation complete.")
    
    train_loader = create_dataloader(X_train, y_train, batch_size, shuffle=True, num_workers=num_workers)
    val_loader = create_dataloader(X_val, y_val, batch_size, shuffle=False, num_workers=num_workers)
    test_loader = create_dataloader(X_test, y_test, batch_size, shuffle=False, num_workers=num_workers)
    
    pipeline_config = {
        'X_min': X_min.tolist(),
        'X_max': X_max.tolist()
    }
    
    return train_loader, val_loader, test_loader, pipeline_config


def prepare_test_data(data_dir, X_min=None, X_max=None, batch_size=64, num_workers=4, test_max_files=None):
    test_partitions = ['partition5']
    print("Selecting test files...")
    test_files, _ = _get_partition_files(data_dir, test_partitions)
    if test_max_files is not None:
        idx = np.random.choice(len(test_files), test_max_files, replace=False)
        test_files = test_files[idx]
        
    print(f"Loading {len(test_files)} test files into RAM...")
    X_test = load_files_to_matrix(test_files)
    y_test = np.array([TargetExtractor.extract_binary(f) for f in test_files])
    
    print("Removing mostly bad instances from test set...")
    X_test, good_mask = remove_mostly_bad(X_test)
    y_test = y_test[good_mask]
    
    print("Applying official_nan_to_num to test...")
    X_test = official_nan_to_num(X_test)
    
    if X_min is not None and X_max is not None:
        print("Transforming test using normalization parameters...")
        X_test = transform_minmax(X_test, X_min, X_max)
    
    test_loader = create_dataloader(X_test, y_test, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return test_loader

