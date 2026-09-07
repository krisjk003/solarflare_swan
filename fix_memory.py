import re

with open("scripts/run_int8_experiment.py", "r") as f:
    code = f.read()

replacement = """            best_int8_threshold = thresh
            
    print(f"[Threshold Optimization] Best INT8 Threshold from P4 = {best_int8_threshold:.4f} (TSS={best_p4_tss:.4f})")

    # Clear P4 validation data from memory to prevent OOM
    del val_loader, val_probs, val_targets
    import gc
    gc.collect()

    # Step 6: Full P5 Test Set Evaluation"""

code = code.replace('            best_int8_threshold = thresh\n            \n    print(f"[Threshold Optimization] Best INT8 Threshold from P4 = {best_int8_threshold:.4f} (TSS={best_p4_tss:.4f})")\n\n    # Step 6: Full P5 Test Set Evaluation', replacement)

with open("scripts/run_int8_experiment.py", "w") as f:
    f.write(code)
