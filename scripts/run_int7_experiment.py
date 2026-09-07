import sys
import os
import argparse
import time
import json
from unittest.mock import patch
import torch
import torch.nn as nn
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.custom_cnn1d import CustomCNN1D
from models.custom_cnn1d_int7 import CustomCNN1D_INT7
from models.quantization import quantize_int7, dequantize_int7
from scripts.quantize import build_fused_fp32_model, run_calibration, convert_to_int7
from scripts.export_hls import export_hls_from_model
from data.dataset import _get_partition_files, load_files_to_matrix, prepare_test_data
from data.preprocess import remove_mostly_bad, official_nan_to_num, transform_minmax
from scripts.train import calculate_metrics

def prepare_p1_p3_calibration_data(data_dir, calib_partitions, checkpoint_prep, calibration_samples=1000, batch_size=64):
    """
    Loads calibration samples from P1-P3 ONLY with explicit P4/P5 protection.
    Reuses frozen preprocessing parameters from the checkpoint without refitting.
    """
    # Strict partition guards
    partitions_list = [p.strip() for p in calib_partitions.split(',')]
    for p in partitions_list:
        if str(p) in ['4', '5']:
            raise ValueError(f"CRITICAL ERROR: Partition {p} is strictly forbidden from calibration!")
            
    partition_dirs = [f"partition{p}" for p in partitions_list]
    print(f"[Calibration] Querying files from partitions: {partition_dirs}")
    all_files, _ = _get_partition_files(data_dir, partition_dirs)
    
    # Path guard
    safe_files = []
    for f in all_files:
        if 'partition4' in f or 'partition5' in f:
            raise ValueError(f"CRITICAL ERROR: Forbidden partition found in calibration file list: {f}")
        safe_files.append(f)
    all_files = np.array(safe_files)
    
    if len(all_files) == 0:
        raise FileNotFoundError(f"No calibration files found in {partition_dirs}")
        
    # Deterministic sampling
    rng = np.random.default_rng(seed=42)
    if calibration_samples is not None and calibration_samples < len(all_files):
        idx = rng.choice(len(all_files), calibration_samples, replace=False)
        selected_files = all_files[idx]
    else:
        selected_files = all_files
        
    print(f"[Calibration] Deterministically selected {len(selected_files)} raw files for calibration.")
    X_calib = load_files_to_matrix(selected_files)
    
    # Apply standard cleaning
    X_calib, _ = remove_mostly_bad(X_calib)
    
    # Extract frozen parameters (handling both naming schemes)
    fallback_mean = np.array(checkpoint_prep['fallback_mean'])
    min_val = np.array(checkpoint_prep.get('min_val', checkpoint_prep.get('X_min')))
    max_val = np.array(checkpoint_prep.get('max_val', checkpoint_prep.get('X_max')))
    
    if fallback_mean is None or min_val is None or max_val is None:
        raise ValueError("Missing essential preprocessing parameters in checkpoint!")
        
    print("[Calibration] Applying frozen preprocessing transforms (no refitting)...")
    X_calib = official_nan_to_num(X_calib, fallback_mean=fallback_mean)
    X_calib = transform_minmax(X_calib, min_val, max_val)
    
    print(f"[Calibration] Prepared {len(X_calib)} calibration tensors of shape {X_calib.shape[1:]}.")
    
    # Wrap in dataloader without labels
    dummy_y = torch.zeros(len(X_calib))
    calib_dataset = torch.utils.data.TensorDataset(torch.tensor(X_calib, dtype=torch.float32), dummy_y)
    calib_loader = torch.utils.data.DataLoader(calib_dataset, batch_size=batch_size, shuffle=False)
    
    return calib_loader, len(selected_files)

def validate_int7_model(int7_model):
    """
    Performs rigorous static validation of the INT7 model topology, parameters,
    and execution path before P5 evaluation.
    """
    print("\n--- Validating INT7 Model Architecture and Parameters ---")
    # 1. Check weight ranges
    for name, module in int7_model.named_modules():
        if hasattr(module, 'weight_int7'):
            w = module.weight_int7
            min_w, max_w = w.min().item(), w.max().item()
            assert min_w >= -64 and max_w <= 63, f"Weight out of INT7 bounds in {name}: [{min_w}, {max_w}]"
            assert w.dtype == torch.int8, f"Weight dtype is {w.dtype}, expected torch.int8 in {name}"
            
        if hasattr(module, 'bias_int32') and module.bias_int32 is not None:
            b = module.bias_int32
            assert b.dtype == torch.int32, f"Bias dtype is {b.dtype}, expected torch.int32 in {name}"
            assert torch.isfinite(b.float()).all(), f"Non-finite bias in {name}"
            
        if hasattr(module, 'input_scale'):
            s_in = module.input_scale.item()
            assert s_in > 0 and np.isfinite(s_in), f"Invalid input scale {s_in} in {name}"
        if hasattr(module, 'output_scale'):
            s_out = module.output_scale.item()
            assert s_out > 0 and np.isfinite(s_out), f"Invalid output scale {s_out} in {name}"
        if hasattr(module, 'multiplier'):
            m = module.multiplier.item()
            assert m >= 0 and np.isfinite(m), f"Invalid multiplier {m} in {name}"
        if hasattr(module, 'shift'):
            s = module.shift.item()
            assert s >= 0 and np.isfinite(s), f"Invalid shift {s} in {name}"

    # 2. Check no BatchNorm or Dropout in graph
    for mod in int7_model.modules():
        assert not isinstance(mod, (nn.BatchNorm1d, nn.BatchNorm2d)), "Found BatchNorm in INT7 model!"
        assert not isinstance(mod, (nn.Dropout, nn.Dropout2d)), "Found Dropout in INT7 model!"
        
    # 3. Check execution path has no FP32 kernels
    with patch('torch.nn.functional.conv1d', side_effect=RuntimeError("F.conv1d called!")):
        with patch('torch.nn.functional.linear', side_effect=RuntimeError("F.linear called!")):
            with patch('torch.nn.functional.max_pool1d', side_effect=RuntimeError("F.max_pool1d called!")):
                dummy_x = torch.randint(-64, 63, (2, 24, 60), dtype=torch.int8)
                dummy_out = int7_model(dummy_x)
                assert dummy_out.shape == (2, 1), f"Expected output shape [2, 1], got {dummy_out.shape}"
                assert dummy_out.dtype == torch.int8, f"Expected output dtype torch.int8, got {dummy_out.dtype}"
                
    print("[Validation Passed] All INT7 weights, INT32 biases, scales, multipliers, and pure integer operations verified.")

def main():
    parser = argparse.ArgumentParser(description="Standalone Real INT7 Post-Training Quantization Experiment")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/custom_cnn1d_best_leakage_free.pt", help="Path to frozen FP32 checkpoint")
    parser.add_argument("--data_dir", type=str, default="data/raw/SWAN-SF", help="Root SWAN-SF data directory")
    parser.add_argument("--calibration_samples", type=int, default=1000, help="Number of samples from P1-P3 for calibration")
    parser.add_argument("--calib_partitions", type=str, default="1,2,3", help="Calibration partitions (strictly P1-P3)")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size for calibration and evaluation")
    parser.add_argument("--output_dir", type=str, default="results/int7_real", help="Directory to save experimental results")
    parser.add_argument("--checkpoint_dir", type=str, default="checkpoints/int7_real", help="Directory to save the INT7 checkpoint")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    
    print("=================================================================")
    print("       STARTING REAL INT7 POST-TRAINING QUANTIZATION EXPERIMENT   ")
    print("=================================================================")

    # Step 1: Pre-run Safety Verifications
    print("\n[Step 1/6] Safety and Precondition Verifications...")
    if not os.path.exists(args.checkpoint):
        raise FileNotFoundError(f"Canonical FP32 checkpoint not found: {args.checkpoint}")
        
    for p in [1, 2, 3]:
        p_dir = os.path.join(args.data_dir, f"partition{p}")
        if not os.path.exists(p_dir):
            raise FileNotFoundError(f"Required training partition {p} directory not found: {p_dir}")
            
    p5_dir = os.path.join(args.data_dir, "partition5")
    if not os.path.exists(p5_dir):
        raise FileNotFoundError(f"Test partition 5 directory not found: {p5_dir}")
        
    print(f"Loading frozen FP32 checkpoint from: {args.checkpoint}")
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    
    if "threshold" not in checkpoint:
        raise KeyError("Checkpoint missing 'threshold' attribute!")
    if "preprocessing" not in checkpoint:
        raise KeyError("Checkpoint missing 'preprocessing' configuration!")
        
    eval_threshold = float(checkpoint["threshold"])
    preprocessing_config = checkpoint["preprocessing"]
    print(f"Frozen FP32 decision threshold (from P4): {eval_threshold:.4f}")
    
    # Step 2: Build FP32 Model and Fuse BatchNorm
    print("\n[Step 2/6] Loading FP32 CustomCNN1D and Fusing BatchNorm...")
    fp32_model = CustomCNN1D(in_channels=24)
    fp32_model.load_state_dict(checkpoint["model_state_dict"])
    fp32_model.eval()
    
    fused_model = build_fused_fp32_model(fp32_model)
    fused_model.eval()
    
    # Step 3: Prepare Calibration Data (P1-P3 only) and Run Calibration
    print("\n[Step 3/6] Preparing P1-P3 Calibration Data and Computing Dynamic Ranges...")
    calib_loader, num_calib_files = prepare_p1_p3_calibration_data(
        args.data_dir,
        args.calib_partitions,
        preprocessing_config,
        calibration_samples=args.calibration_samples,
        batch_size=args.batch_size
    )
    
    t_calib_start = time.time()
    act_max = run_calibration(fused_model, calib_loader, device=torch.device("cpu"))
    t_calib = time.time() - t_calib_start
    print(f"[Calibration] Completed in {t_calib:.2f} seconds.")
    
    # Step 4: Convert to CustomCNN1D_INT7 and Validate
    print("\n[Step 4/6] Converting to True Integer CustomCNN1D_INT7 Model...")
    int7_model = convert_to_int7(fused_model, act_max)
    int7_model.eval()
    
    # Validate INT7 properties
    validate_int7_model(int7_model)
    
    # Save the new real INT7 checkpoint
    int7_checkpoint_path = os.path.join(args.checkpoint_dir, "custom_cnn1d_int7_real.pt")
    torch.save({
        'model_state_dict': int7_model.state_dict(),
        'act_max_dict': act_max,
        'calib_partitions': args.calib_partitions,
        'calibration_samples': num_calib_files,
        'preprocessing': preprocessing_config,
        'threshold': eval_threshold,
        'fp32_source_checkpoint': args.checkpoint,
        'creation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }, int7_checkpoint_path)
    print(f"[Checkpoint Saved] Real INT7 model saved to: {int7_checkpoint_path}")
    
    # Export HLS artifacts
    hls_dir = os.path.join(args.output_dir, "hls")
    export_hls_from_model(int7_model, out_dir=hls_dir)
    
    # Save scales and calibration metadata
    scales_dict = {k: float(v / 63.0) for k, v in act_max.items()}
    scales_path = os.path.join(args.output_dir, "scales.json")
    with open(scales_path, "w") as sf:
        json.dump(scales_dict, sf, indent=2)
        
    calib_meta_path = os.path.join(args.output_dir, "calibration_metadata.json")
    with open(calib_meta_path, "w") as cmf:
        json.dump({
            "calibration_partitions": args.calib_partitions,
            "calibration_samples_requested": args.calibration_samples,
            "calibration_samples_used": num_calib_files,
            "calibration_time_seconds": t_calib,
            "act_max": act_max,
            "input_scale": float(int7_model.input_scale.item()),
            "fc2_output_scale": float(int7_model.fc2.output_scale.item())
        }, cmf, indent=2)

    # Step 5: Full P5 Test Set Evaluation
    print("\n[Step 5/6] Preparing Full Partition 5 Test Dataset...")
    min_val = np.array(preprocessing_config.get('min_val', preprocessing_config.get('X_min')))
    max_val = np.array(preprocessing_config.get('max_val', preprocessing_config.get('X_max')))
    fallback_mean = np.array(preprocessing_config.get('fallback_mean'))
    
    t_load_p5_start = time.time()
    test_loader = prepare_test_data(
        args.data_dir,
        X_min=min_val,
        X_max=max_val,
        fallback_mean=fallback_mean,
        batch_size=args.batch_size,
        num_workers=4
    )
    t_load_p5 = time.time() - t_load_p5_start
    print(f"[P5 Dataset] Loaded in {t_load_p5:.2f} seconds.")
    
    print("\n[Step 6/6] Executing True INT7 Inference on Full Partition 5...")
    test_probs = []
    test_targets = []
    
    t_eval_start = time.time()
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            # 1. Quantize preprocessed input to INT7
            x_int7 = quantize_int7(batch_x, int7_model.input_scale.item())
            
            # 2. Pure integer forward pass
            out_int7 = int7_model(x_int7)
            
            # 3. Dequantize final output logit to float & compute probability
            logits = dequantize_int7(out_int7, int7_model.fc2.output_scale.item())
            probs = torch.sigmoid(logits)
            
            test_probs.append(probs.cpu())
            test_targets.append(batch_y.unsqueeze(1).cpu())
            
    t_eval = time.time() - t_eval_start
    
    test_probs = torch.cat(test_probs).squeeze()
    test_targets = torch.cat(test_targets).squeeze()
    
    total_samples = len(test_targets)
    pos_count = int((test_targets == 1.0).sum().item())
    neg_count = int((test_targets == 0.0).sum().item())
    
    # Calculate metrics with frozen threshold
    metrics = calculate_metrics(test_targets, test_probs, threshold=eval_threshold)
    
    # FP32 baseline reference metrics
    fp32_tss = 0.8617
    fp32_auc = 0.9781
    fp32_precision = 0.1648
    fp32_recall = 0.9242
    fp32_f1 = 0.2798
    fp32_tp = 915
    fp32_tn = 69487
    fp32_fp = 4636
    fp32_fn = 75
    
    tss_diff = metrics['tss'] - fp32_tss
    
    results_summary = (
        "=================================================================\n"
        "             REAL INT7 EVALUATION ON FULL PARTITION 5            \n"
        "=================================================================\n"
        f"Calibration Partitions: {args.calib_partitions}\n"
        f"Calibration Samples Used: {num_calib_files}\n"
        f"Selected Decision Threshold (frozen from P4): {eval_threshold:.4f}\n"
        f"Total P5 Test Samples: {total_samples}\n"
        f"Positive Samples (M/X): {pos_count}\n"
        f"Negative Samples (Q/B/C): {neg_count}\n"
        f"INT7 P5 TSS: {metrics['tss']:.4f}\n"
        f"INT7 P5 AUC: {metrics['auc']:.4f}\n"
        f"INT7 P5 Precision: {metrics['precision']:.4f}\n"
        f"INT7 P5 Recall: {metrics['recall']:.4f}\n"
        f"INT7 P5 F1: {metrics['f1']:.4f}\n"
        f"TP: {metrics['tp']}, TN: {metrics['tn']}, FP: {metrics['fp']}, FN: {metrics['fn']}\n"
        f"INT7 P5 Inference Time: {t_eval:.2f} seconds\n"
        "=================================================================\n"
        "                  INT7 vs FP32 BASELINE COMPARISON               \n"
        "=================================================================\n"
        f"FP32 Baseline TSS: {fp32_tss:.4f}\n"
        f"INT7 Quantized TSS: {metrics['tss']:.4f}\n"
        f"TSS Delta (INT7 - FP32): {tss_diff:+.4f}\n"
        f"FP32 Baseline AUC: {fp32_auc:.4f} | INT7 AUC: {metrics['auc']:.4f} (Delta: {metrics['auc'] - fp32_auc:+.4f})\n"
        f"FP32 Precision:    {fp32_precision:.4f} | INT7 Precision: {metrics['precision']:.4f}\n"
        f"FP32 Recall:       {fp32_recall:.4f} | INT7 Recall:    {metrics['recall']:.4f}\n"
        f"FP32 F1 Score:     {fp32_f1:.4f} | INT7 F1 Score:  {metrics['f1']:.4f}\n"
        f"Confusion Matrix Comparison:\n"
        f"  FP32: TP={fp32_tp}, TN={fp32_tn}, FP={fp32_fp}, FN={fp32_fn}\n"
        f"  INT7: TP={metrics['tp']}, TN={metrics['tn']}, FP={metrics['fp']}, FN={metrics['fn']}\n"
        "=================================================================\n"
    )
    
    p5_results_path = os.path.join(args.output_dir, "int7_p5_results.txt")
    with open(p5_results_path, "w") as rf:
        rf.write(results_summary)
        
    vs_fp32_path = os.path.join(args.output_dir, "int7_vs_fp32.txt")
    with open(vs_fp32_path, "w") as vf:
        vf.write(results_summary)
        
    print("\n" + results_summary)
    print(f"Results saved to: {p5_results_path} and {vs_fp32_path}")

if __name__ == "__main__":
    main()
