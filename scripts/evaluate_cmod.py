import sys
import os
import argparse
import time
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.dataset import prepare_test_data
from models.cmod import Cmod
from scripts.train_cmod import calculate_metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--data_dir", type=str, default="data/raw/SWAN-SF")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/cmod_best.pt")
    args = parser.parse_args()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluation Device: {device}")
    
    if not os.path.exists(args.checkpoint):
        raise FileNotFoundError(f"Checkpoint not found at: {args.checkpoint}")
        
    print(f"Loading checkpoint from {args.checkpoint}...")
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    preprocessing_config = checkpoint.get('preprocessing', {})
    
    X_min = np.array(preprocessing_config['min_val']) if 'min_val' in preprocessing_config and preprocessing_config['min_val'] is not None else None
    X_max = np.array(preprocessing_config['max_val']) if 'max_val' in preprocessing_config and preprocessing_config['max_val'] is not None else None
    
    print(f"Preparing full Partition 5 test dataset...")
    test_loader = prepare_test_data(
        args.data_dir,
        X_min=X_min,
        X_max=X_max,
        batch_size=args.batch_size,
        num_workers=4 if torch.cuda.is_available() else 0
    )
    
    # Instantiate Model
    model = Cmod(in_channels=24)
    dummy_x = torch.randn(2, 24, 60)
    model.initialize_lazy_layers(dummy_x)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    test_probs = []
    test_targets = []
    
    start_time = time.time()
    
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(device) # [B, 24, 60]
            batch_y = batch_y.unsqueeze(1)
            
            logits = model(batch_x)
            probs = torch.sigmoid(logits)
            
            test_probs.append(probs.cpu())
            test_targets.append(batch_y.cpu())
            
    eval_time = time.time() - start_time
    
    test_probs = torch.cat(test_probs).squeeze()
    test_targets = torch.cat(test_targets).squeeze()
    
    total_samples = len(test_targets)
    pos_count = int((test_targets == 1.0).sum().item())
    neg_count = int((test_targets == 0.0).sum().item())
    
    metrics = calculate_metrics(test_targets, test_probs, threshold=0.5)
    
    os.makedirs("results/tables", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)
    
    best_val_tss = checkpoint.get('best_val_tss', 'N/A')
    best_epoch = checkpoint.get('epoch', 'N/A')
    
    results_text = (
        "=== Cmod Final Evaluation on P5 ===\n"
        f"Best Validation TSS: {best_val_tss}\n"
        f"Best Epoch: {best_epoch}\n"
        f"Total Test Samples: {total_samples}\n"
        f"Positive Samples (M/X): {pos_count}\n"
        f"Negative Samples (Q/B/C): {neg_count}\n"
        f"P5 TSS: {metrics['tss']:.4f}\n"
        f"P5 AUC: {metrics['auc']:.4f}\n"
        f"P5 Precision: {metrics['precision']:.4f}\n"
        f"P5 Recall: {metrics['recall']:.4f}\n"
        f"P5 F1: {metrics['f1']:.4f}\n"
        f"TP: {metrics['tp']}, TN: {metrics['tn']}, FP: {metrics['fp']}, FN: {metrics['fn']}\n"
        f"Evaluation Time: {eval_time:.2f} seconds\n"
    )
    
    with open("results/tables/cmod_final_results.txt", "w") as f:
        f.write(results_text)
        
    print("\n" + results_text)
    
    # ROC Curve Plot
    desc_score_indices = torch.argsort(test_probs, descending=True)
    y_true_sorted = test_targets[desc_score_indices]
    tps = torch.cumsum(y_true_sorted, dim=0)
    fps = torch.cumsum(1.0 - y_true_sorted, dim=0)
    tpr_curve = tps / tps[-1] if tps[-1] > 0 else tps
    fpr_curve = fps / fps[-1] if fps[-1] > 0 else fps
    
    plt.figure()
    plt.plot(fpr_curve.numpy(), tpr_curve.numpy(), label=f"AUC = {metrics['auc']:.4f}")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - P5 Test Set')
    plt.legend()
    plt.savefig("results/figures/cmod_roc_curve.png")
    plt.close()
    
    # Confusion Matrix Plot
    fig, ax = plt.subplots()
    cax = ax.matshow([[metrics['tn'], metrics['fp']], [metrics['fn'], metrics['tp']]], cmap=plt.cm.Blues)
    fig.colorbar(cax)
    
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Negative', 'Positive'])
    ax.set_yticklabels(['Negative', 'Positive'])
    
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix - P5 Test Set')
    
    for i in range(2):
        for j in range(2):
            val = [[metrics['tn'], metrics['fp']], [metrics['fn'], metrics['tp']]][i][j]
            ax.text(j, i, str(val), va='center', ha='center', 
                    color='black' if val < (total_samples / 4) else 'white')
            
    plt.savefig("results/figures/cmod_confusion_matrix.png")
    plt.close()

if __name__ == "__main__":
    main()
