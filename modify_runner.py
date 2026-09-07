import re

with open("scripts/run_int8_experiment.py", "r") as f:
    code = f.read()

# Fix imports
code = code.replace("from data.preprocess import remove_mostly_bad, official_nan_to_num, transform_minmax",
                    "from data.preprocess import remove_mostly_bad, official_nan_to_num, transform_minmax, TargetExtractor")

# Insert prepare_validation_data_for_threshold after validate_int7_model = validate_int8_model
prep_val = """
def prepare_validation_data_for_threshold(data_dir, min_val, max_val, fallback_mean, batch_size=64):
    print("[Threshold Optimization] Selecting P4 validation files...")
    val_files, _ = _get_partition_files(data_dir, ['partition4'])
    
    print(f"[Threshold Optimization] Loading {len(val_files)} P4 validation files into RAM...")
    X_val = load_files_to_matrix(val_files)
    y_val = np.array([TargetExtractor.extract_binary(f) for f in val_files])
    
    print("[Threshold Optimization] Removing mostly bad instances from validation set...")
    X_val, good_mask = remove_mostly_bad(X_val)
    y_val = y_val[good_mask]
    
    print("[Threshold Optimization] Applying frozen preprocessing to P4...")
    X_val = official_nan_to_num(X_val, fallback_mean=fallback_mean)
    X_val = transform_minmax(X_val, min_val, max_val)
    
    val_dataset = torch.utils.data.TensorDataset(
        torch.tensor(X_val, dtype=torch.float32), 
        torch.tensor(y_val, dtype=torch.float32)
    )
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    
    return val_loader
"""
code = code.replace("validate_int7_model = validate_int8_model", "validate_int7_model = validate_int8_model\n" + prep_val)


# Split at Step 5
parts = code.split('    # Step 5: Full P5 Test Set Evaluation')
prefix = parts[0]

new_suffix = """    # Step 5: Optimize INT8 Threshold on P4
    print("\\n[Step 5/7] Preparing P4 Validation Dataset for INT8 Threshold Sweep...")
    min_val = np.array(preprocessing_config.get('min_val', preprocessing_config.get('X_min')))
    max_val = np.array(preprocessing_config.get('max_val', preprocessing_config.get('X_max')))
    fallback_mean = np.array(preprocessing_config.get('fallback_mean'))
    
    val_loader = prepare_validation_data_for_threshold(
        args.data_dir, min_val, max_val, fallback_mean, batch_size=args.batch_size
    )
    
    print("\\n[Step 5/7] Running P4 Validation Inference...")
    val_probs = []
    val_targets = []
    with torch.no_grad():
        for batch_x, batch_y in val_loader:
            x_int8 = quantize_int8(batch_x, int8_model.input_scale.item())
            out_int8 = int8_model(x_int8)
            logits = dequantize_int8(out_int8, int8_model.fc2.output_scale.item())
            probs = torch.sigmoid(logits)
            
            val_probs.append(probs.cpu())
            val_targets.append(batch_y.unsqueeze(1).cpu())
            
    val_probs = torch.cat(val_probs).squeeze()
    val_targets = torch.cat(val_targets).squeeze()
    
    print("[Threshold Optimization] Sweeping thresholds on P4 [0.1, 0.9]...")
    best_p4_tss = -1.0
    best_int8_threshold = 0.5
    for thresh in np.linspace(0.1, 0.9, 81):
        temp_metrics = calculate_metrics(val_targets, val_probs, threshold=thresh)
        if temp_metrics['tss'] > best_p4_tss:
            best_p4_tss = temp_metrics['tss']
            best_int8_threshold = thresh
            
    print(f"[Threshold Optimization] Best INT8 Threshold from P4 = {best_int8_threshold:.4f} (TSS={best_p4_tss:.4f})")

    # Step 6: Full P5 Test Set Evaluation
    print("\\n[Step 6/7] Preparing Full Partition 5 Test Dataset...")
    
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
    
    print("\\n[Step 7/7] Executing True INT8 Inference on Full Partition 5...")
    test_probs = []
    test_targets = []
    
    t_eval_start = time.time()
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            # 1. Quantize preprocessed input to INT8
            x_int8 = quantize_int8(batch_x, int8_model.input_scale.item())
            
            # 2. Pure integer forward pass
            out_int8 = int8_model(x_int8)
            
            # 3. Dequantize final output logit to float & compute probability
            logits = dequantize_int8(out_int8, int8_model.fc2.output_scale.item())
            probs = torch.sigmoid(logits)
            
            test_probs.append(probs.cpu())
            test_targets.append(batch_y.unsqueeze(1).cpu())
            
    t_eval = time.time() - t_eval_start
    
    test_probs = torch.cat(test_probs).squeeze()
    test_targets = torch.cat(test_targets).squeeze()
    
    total_samples = len(test_targets)
    pos_count = int((test_targets == 1.0).sum().item())
    neg_count = int((test_targets == 0.0).sum().item())
    
    # Calculate metrics for both threshold strategies
    metrics_fp32_thresh = calculate_metrics(test_targets, test_probs, threshold=eval_threshold)
    metrics_int8_thresh = calculate_metrics(test_targets, test_probs, threshold=best_int8_threshold)
    
    # Correct FP32 baseline reference metrics
    fp32_tss = 0.8685
    fp32_auc = 0.9747
    fp32_precision = 0.1765
    fp32_recall = 0.9263
    fp32_f1 = 0.2965
    fp32_tp = 917
    fp32_tn = 69845
    fp32_fp = 4278
    fp32_fn = 73
    
    tss_diff_fp32_thresh = metrics_fp32_thresh['tss'] - fp32_tss
    tss_diff_int8_thresh = metrics_int8_thresh['tss'] - fp32_tss
    
    results_summary = (
        "=============================================================\\n"
        "INT8 P5 — FROZEN FP32 THRESHOLD\\n"
        "===============================\\n"
        f"Threshold: {eval_threshold:.4f}\\n"
        f"TSS: {metrics_fp32_thresh['tss']:.4f}\\n"
        f"AUC: {metrics_fp32_thresh['auc']:.4f}\\n"
        f"Precision: {metrics_fp32_thresh['precision']:.4f}\\n"
        f"Recall: {metrics_fp32_thresh['recall']:.4f}\\n"
        f"F1: {metrics_fp32_thresh['f1']:.4f}\\n"
        f"TP: {metrics_fp32_thresh['tp']}, TN: {metrics_fp32_thresh['tn']}, FP: {metrics_fp32_thresh['fp']}, FN: {metrics_fp32_thresh['fn']}\\n"
        "\\n"
        "=============================================================\\n"
        "INT8 P4 — OPTIMIZED THRESHOLD SEARCH\\n"
        "====================================\\n"
        f"Best P4 threshold: {best_int8_threshold:.4f}\\n"
        f"Best P4 TSS: {best_p4_tss:.4f}\\n"
        "\\n"
        "=============================================================\\n"
        "INT8 P5 — INT8-OPTIMIZED THRESHOLD\\n"
        "==================================\\n"
        f"Threshold: {best_int8_threshold:.4f}\\n"
        f"TSS: {metrics_int8_thresh['tss']:.4f}\\n"
        f"AUC: {metrics_int8_thresh['auc']:.4f}\\n"
        f"Precision: {metrics_int8_thresh['precision']:.4f}\\n"
        f"Recall: {metrics_int8_thresh['recall']:.4f}\\n"
        f"F1: {metrics_int8_thresh['f1']:.4f}\\n"
        f"TP: {metrics_int8_thresh['tp']}, TN: {metrics_int8_thresh['tn']}, FP: {metrics_int8_thresh['fp']}, FN: {metrics_int8_thresh['fn']}\\n"
        "\\n"
        "=============================================================\\n"
        "FINAL FP32 vs INT8 COMPARISON\\n"
        "=============================\\n"
        f"{'Metric':<15} | {'FP32 Base':<10} | {'INT8@FP32-Th':<15} | {'INT8@INT8-Th':<15}\\n"
        f"{'-'*65}\\n"
        f"{'Threshold':<15} | {eval_threshold:<10.4f} | {eval_threshold:<15.4f} | {best_int8_threshold:<15.4f}\\n"
        f"{'TSS':<15} | {fp32_tss:<10.4f} | {metrics_fp32_thresh['tss']:<15.4f} | {metrics_int8_thresh['tss']:<15.4f}\\n"
        f"{'AUC':<15} | {fp32_auc:<10.4f} | {metrics_fp32_thresh['auc']:<15.4f} | {metrics_int8_thresh['auc']:<15.4f}\\n"
        f"{'Precision':<15} | {fp32_precision:<10.4f} | {metrics_fp32_thresh['precision']:<15.4f} | {metrics_int8_thresh['precision']:<15.4f}\\n"
        f"{'Recall':<15} | {fp32_recall:<10.4f} | {metrics_fp32_thresh['recall']:<15.4f} | {metrics_int8_thresh['recall']:<15.4f}\\n"
        f"{'F1':<15} | {fp32_f1:<10.4f} | {metrics_fp32_thresh['f1']:<15.4f} | {metrics_int8_thresh['f1']:<15.4f}\\n"
        f"{'TP':<15} | {fp32_tp:<10} | {metrics_fp32_thresh['tp']:<15} | {metrics_int8_thresh['tp']:<15}\\n"
        f"{'TN':<15} | {fp32_tn:<10} | {metrics_fp32_thresh['tn']:<15} | {metrics_int8_thresh['tn']:<15}\\n"
        f"{'FP':<15} | {fp32_fp:<10} | {metrics_fp32_thresh['fp']:<15} | {metrics_int8_thresh['fp']:<15}\\n"
        f"{'FN':<15} | {fp32_fn:<10} | {metrics_fp32_thresh['fn']:<15} | {metrics_int8_thresh['fn']:<15}\\n"
        "=============================================================\\n"
    )
    
    p5_results_path = os.path.join(args.output_dir, "int8_p5_results.txt")
    with open(p5_results_path, "w") as rf:
        rf.write(results_summary)
        
    vs_fp32_path = os.path.join(args.output_dir, "int8_vs_fp32.txt")
    with open(vs_fp32_path, "w") as vf:
        vf.write(results_summary)
        
    print("\\n" + results_summary)
    print(f"Results saved to: {p5_results_path} and {vs_fp32_path}")

if __name__ == "__main__":
    main()
"""

with open("scripts/run_int8_experiment.py", "w") as f:
    f.write(prefix + new_suffix)

