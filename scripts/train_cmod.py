import sys
import os
import argparse
import random
import time
import torch
import torch.nn as nn
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.dataset import prepare_data
from models.cmod import Cmod

def seed_everything(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

from sklearn.metrics import roc_auc_score

def calculate_metrics(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).float()
    
    tp = ((y_pred == 1) & (y_true == 1)).sum().item()
    tn = ((y_pred == 0) & (y_true == 0)).sum().item()
    fp = ((y_pred == 1) & (y_true == 0)).sum().item()
    fn = ((y_pred == 0) & (y_true == 1)).sum().item()
    
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tss = tpr - fpr
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tpr
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Calculate ROC-AUC using sklearn
    try:
        # Handle case where validation contains only one class
        if len(torch.unique(y_true)) > 1:
            auc = roc_auc_score(y_true.numpy(), y_prob.numpy())
        else:
            auc = 0.5 # Undefined AUC for single class
    except ValueError:
        auc = 0.5
    
    return {
        "tss": tss,
        "auc": auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--patience", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data_dir", type=str, default="data/raw/SWAN-SF")
    args = parser.parse_args()
    
    seed_everything(args.seed)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        
    print("\nPreparing dataloaders...")
    train_loader, val_loader, _, pipeline_config = prepare_data(
        args.data_dir, 
        batch_size=args.batch_size, 
        num_workers=4 if torch.cuda.is_available() else 0
    )
    
    model = Cmod(in_channels=24)
    
    # Initialize LazyLinear
    dummy_x = torch.randn(2, 24, 60)
    model.initialize_lazy_layers(dummy_x)
    
    model.to(device)
    
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    
    best_val_tss = -1.0
    best_epoch = -1
    epochs_no_improve = 0
    
    os.makedirs("checkpoints", exist_ok=True)
    
    start_time = time.time()
    
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device) # [B, 24, 60]
            batch_y = batch_y.unsqueeze(1).to(device)
            
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * batch_x.size(0)
            
        train_loss /= len(train_loader.dataset)
        
        model.eval()
        val_loss = 0.0
        val_probs = []
        val_targets = []
        
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.unsqueeze(1).to(device)
                
                logits = model(batch_x)
                loss = criterion(logits, batch_y)
                val_loss += loss.item() * batch_x.size(0)
                
                probs = torch.sigmoid(logits)
                val_probs.append(probs.cpu())
                val_targets.append(batch_y.cpu())
                
        val_loss /= len(val_loader.dataset)
        
        val_probs = torch.cat(val_probs)
        val_targets = torch.cat(val_targets)
        
        metrics = calculate_metrics(val_targets.squeeze(), val_probs.squeeze())
        
        print(f"Epoch {epoch}/{args.epochs}")
        print(f"Train Loss: {train_loss:.4f}")
        print(f"Val Loss: {val_loss:.4f}")
        print(f"Val TSS: {metrics['tss']:.4f}")
        print(f"Val AUC: {metrics['auc']:.4f}")
        print(f"Val Precision: {metrics['precision']:.4f}")
        print(f"Val Recall: {metrics['recall']:.4f}")
        print(f"Val F1: {metrics['f1']:.4f}")
        print("-" * 30)
        
        if metrics['tss'] > best_val_tss:
            best_val_tss = metrics['tss']
            best_epoch = epoch
            epochs_no_improve = 0
            
            # Extract serializable preprocessing parameters
            preprocessing_config = {
                'method': 'official_cmod_local_avg_min_max',
                'min_val': pipeline_config['X_min'],
                'max_val': pipeline_config['X_max']
            }
            
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_tss': best_val_tss,
                'metrics': metrics,
                'seed': args.seed,
                'preprocessing': preprocessing_config,
            }, "checkpoints/cmod_best.pt")
            print(f"*** New best model saved at epoch {epoch} with Val TSS: {best_val_tss:.4f} ***\n")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= args.patience:
                print(f"Early stopping triggered after {epoch} epochs.")
                break
                
    total_time = time.time() - start_time
    print(f"Training completed in {total_time:.2f} seconds.")
    print(f"Best Validation TSS: {best_val_tss:.4f} at epoch {best_epoch}")

if __name__ == "__main__":
    main()
