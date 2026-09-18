#!/usr/bin/env python3
"""
generate_hls_test_vector.py
────────────────────────────
Generates bit-exact test vectors for HLS C-simulation of CustomCNN1D_INT8.

Inputs used:
  checkpoints/int8_real/custom_cnn1d_int8_real.pt  — frozen INT8 model weights
  data/raw/SWAN-SF/partition5                       — real P5 samples (test set)

Outputs:
  hls/test_input.txt    — 1440 int8 values (24 channels x 60 timesteps), one per line
  hls/test_expected.txt — single int8 logit from model.forward()

Preprocessing pipeline (matching run_int8_experiment.py exactly):
  1. _get_partition_files(data_dir, ['partition5'])
  2. load_files_to_matrix(first_clean_file)
  3. remove_mostly_bad(X)
  4. official_nan_to_num(X, fallback_mean=checkpoint preprocessing)
  5. transform_minmax(X, min_val, max_val)
  6. quantize_int8(x_float, model.input_scale.item())
  7. int8_model(x_int8)  — pure integer forward pass

NO training or quantization is run.
"""
import sys
import os
import numpy as np
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.custom_cnn1d_int8 import CustomCNN1D_INT8
from models.quantization import quantize_int8
from data.dataset import _get_partition_files, load_files_to_matrix
from data.preprocess import remove_mostly_bad, official_nan_to_num, transform_minmax

CHECKPOINT_PATH = "checkpoints/int8_real/custom_cnn1d_int8_real.pt"
DATA_DIR        = "data/raw/SWAN-SF"
INPUT_TXT       = "hls/test_input.txt"
EXPECTED_TXT    = "hls/test_expected.txt"

# Load frozen INT8 checkpoint
print(f"Loading INT8 checkpoint: {CHECKPOINT_PATH}")
assert os.path.exists(CHECKPOINT_PATH), f"Checkpoint not found: {CHECKPOINT_PATH}"
checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)

prep = checkpoint['preprocessing']
fallback_mean = np.array(prep['fallback_mean'])
min_val       = np.array(prep.get('min_val', prep.get('X_min')))
max_val       = np.array(prep.get('max_val', prep.get('X_max')))
print(f"  preprocessing method : {prep.get('method', 'unknown')}")
print(f"  min_val shape        : {min_val.shape}")
print(f"  max_val shape        : {max_val.shape}")

model = CustomCNN1D_INT8(in_channels=24)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()
input_scale = model.input_scale.item()
print(f"  input_scale          : {input_scale:.6e}")

# Load exactly ONE real P5 sample deterministically (first clean file, sorted)
print(f"\nLoading P5 file list from {DATA_DIR}/partition5 ...")
all_files, _ = _get_partition_files(DATA_DIR, ['partition5'])
print(f"  Total P5 files: {len(all_files)}")

all_files_sorted = sorted(all_files.tolist())

sample_file  = None
x_int8_final = None
sample_index = None

for idx, fpath in enumerate(all_files_sorted):
    X_single = load_files_to_matrix(np.array([fpath]))
    X_clean, good_mask = remove_mostly_bad(X_single)
    if len(X_clean) == 0:
        continue
    X_clean = official_nan_to_num(X_clean, fallback_mean=fallback_mean)
    X_clean = transform_minmax(X_clean, min_val, max_val)
    x_float = torch.tensor(X_clean, dtype=torch.float32)
    x_int8  = quantize_int8(x_float, input_scale)
    sample_file  = fpath
    sample_index = idx
    x_int8_final = x_int8
    break

assert x_int8_final is not None, "No clean P5 sample found — check data path."
print(f"  Sample index  : {sample_index}")
print(f"  File          : {os.path.basename(sample_file)}")
print(f"  Input shape   : {x_int8_final.shape}, dtype: {x_int8_final.dtype}")

# Pure integer forward pass — no training, no quantization
print("\nRunning CustomCNN1D_INT8 forward pass ...")
with torch.no_grad():
    y_int8 = model(x_int8_final)

expected_logit = int(y_int8.item())
print(f"  Expected INT8 output logit: {expected_logit}")

# Write hls/test_input.txt
# Flattened C-contiguous: index = c * 60 + t  (matches cnn_hw.cpp access pattern)
flat_input = x_int8_final.squeeze(0).flatten().tolist()
assert len(flat_input) == 24 * 60

os.makedirs("hls", exist_ok=True)
with open(INPUT_TXT, "w") as f:
    for v in flat_input:
        f.write(f"{int(v)}\n")
print(f"\nWrote {len(flat_input)} values -> {INPUT_TXT}")

# Write hls/test_expected.txt
with open(EXPECTED_TXT, "w") as f:
    f.write(f"{expected_logit}\n")
print(f"Wrote expected logit {expected_logit} -> {EXPECTED_TXT}")

print("\n" + "="*60)
print("HLS Test Vector Generation Complete")
print(f"  Checkpoint  : {CHECKPOINT_PATH}")
print(f"  Sample file : {os.path.basename(sample_file)}")
print(f"  Sample index: {sample_index} (first clean P5 file, sorted order)")
print(f"  Input file  : {INPUT_TXT}   ({len(flat_input)} int8 values)")
print(f"  Expected    : {EXPECTED_TXT} (INT8 logit = {expected_logit})")
print("="*60)
print("\nNO training, quantization, or HLS/Vivado was run.")
