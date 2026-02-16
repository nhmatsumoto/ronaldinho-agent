import json
import time
import math
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, Tuple, List, Union

import numpy as np
import pandas as pd

import torch
import torch.nn as nn
import torch.optim as optim

# -----------------------------
# Utilities
# -----------------------------

def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def train_val_test_split(X, y, val_ratio=0.15, test_ratio=0.15, seed=42):
    n = len(X)
    idx = np.arange(n)
    rng = np.random.default_rng(seed)
    rng.shuffle(idx)

    test_n = int(n * test_ratio)
    val_n = int(n * val_ratio)

    test_idx = idx[:test_n]
    val_idx = idx[test_n:test_n + val_n]
    train_idx = idx[test_n + val_n:]

    return (X[train_idx], y[train_idx]), (X[val_idx], y[val_idx]), (X[test_idx], y[test_idx])

def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))

def safe_auc(y_true, y_score) -> Optional[float]:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score)
    pos = y_true == 1
    neg = y_true == 0
    n_pos = pos.sum()
    n_neg = neg.sum()
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(y_score)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(y_score)) + 1
    sum_ranks_pos = ranks[pos].sum()
    auc = (sum_ranks_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)

def confusion_matrix_binary(y_true, y_pred) -> Dict[str, int]:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}

def f1_score_binary(y_true, y_pred) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    tp, fp, fn = cm["tp"], cm["fp"], cm["fn"]
    denom = (2 * tp + fp + fn)
    return float((2 * tp) / denom) if denom > 0 else 0.0

def accuracy(y_true, y_pred) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float((y_true == y_pred).mean())

def rmse(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

def mae(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))

def r2(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

# -----------------------------
# Preprocessing
# -----------------------------

@dataclass
class PreprocessConfig:
    numeric_cols: List[str]
    categorical_cols: List[str]
    cat_topk: int
    numeric_mean: Dict[str, float]
    numeric_std: Dict[str, float]
    cat_maps: Dict[str, Dict[str, int]]
    output_dim: int

def infer_schema(df: pd.DataFrame, target_col: str, features: Optional[List[str]] = None) -> Tuple[List[str], List[str], List[str]]:
    cols = features if features is not None else [c for c in df.columns if c != target_col]
    numeric_cols, categorical_cols = [], []
    for c in cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            numeric_cols.append(c)
        else:
            categorical_cols.append(c)
    return cols, numeric_cols, categorical_cols

def fit_preprocess(df: pd.DataFrame, target_col: str, features: Optional[List[str]] = None, cat_topk: int = 50) -> PreprocessConfig:
    cols, numeric_cols, categorical_cols = infer_schema(df, target_col, features)
    numeric_mean, numeric_std = {}, {}
    for c in numeric_cols:
        v = pd.to_numeric(df[c], errors="coerce")
        m = float(np.nanmean(v.values))
        s = float(np.nanstd(v.values))
        if not np.isfinite(s) or s == 0.0:
            s = 1.0
        numeric_mean[c] = m
        numeric_std[c] = s

    cat_maps: Dict[str, Dict[str, int]] = {}
    cat_dim = 0
    for c in categorical_cols:
        series = df[c].astype(str).fillna("")
        top = series.value_counts().head(cat_topk).index.tolist()
        mapping = {val: i for i, val in enumerate(top)}
        cat_maps[c] = mapping
        cat_dim += (len(mapping) + 1)

    output_dim = len(numeric_cols) + cat_dim
    return PreprocessConfig(
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        cat_topk=cat_topk,
        numeric_mean=numeric_mean,
        numeric_std=numeric_std,
        cat_maps=cat_maps,
        output_dim=output_dim
    )

def transform(df: pd.DataFrame, cfg: PreprocessConfig) -> np.ndarray:
    n = len(df)
    parts = []
    if cfg.numeric_cols:
        num = np.zeros((n, len(cfg.numeric_cols)), dtype=np.float32)
        for j, c in enumerate(cfg.numeric_cols):
            v = pd.to_numeric(df[c], errors="coerce").values.astype(np.float32)
            v = np.where(np.isfinite(v), v, cfg.numeric_mean[c])
            v = (v - cfg.numeric_mean[c]) / cfg.numeric_std[c]
            num[:, j] = v
        parts.append(num)
    for c in cfg.categorical_cols:
        mapping = cfg.cat_maps[c]
        dim = len(mapping) + 1
        oh = np.zeros((n, dim), dtype=np.float32)
        series = df[c].astype(str).fillna("").values
        for i, val in enumerate(series):
            idx = mapping.get(val, len(mapping))
            oh[i, idx] = 1.0
        parts.append(oh)
    if not parts:
        raise ValueError("No features after preprocessing.")
    return np.concatenate(parts, axis=1).astype(np.float32)

# -----------------------------
# Model
# -----------------------------

class SmallMLP(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, hidden: List[int], dropout: float):
        super().__init__()
        layers = []
        prev = in_dim
        for h in hidden:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev = h
        layers.append(nn.Linear(prev, out_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)

# -----------------------------
# Training & Logic
# -----------------------------

@dataclass
class RunResult:
    architecture: Dict[str, Any]
    params_count: int
    train_metrics: Dict[str, float]
    val_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    threshold: Optional[float]
    confusion_matrix: Optional[Dict[str, int]]
    preprocess: Dict[str, Any]
    notes: List[str]
    state_dict: Any = None

def evaluate_classification(logits: np.ndarray, y_true: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
    probs = sigmoid(logits.reshape(-1))
    y_pred = (probs >= threshold).astype(int)
    metrics = {
        "accuracy": accuracy(y_true, y_pred),
        "f1": f1_score_binary(y_true, y_pred),
    }
    auc = safe_auc(y_true, probs)
    if auc is not None:
        metrics["roc_auc"] = auc
    return {"metrics": metrics, "cm": confusion_matrix_binary(y_true, y_pred)}

def pick_threshold_for_f1(logits: np.ndarray, y_true: np.ndarray) -> float:
    probs = sigmoid(logits.reshape(-1))
    best_t, best_f1 = 0.5, -1.0
    for t in np.linspace(0.05, 0.95, 19):
        y_pred = (probs >= t).astype(int)
        f1 = f1_score_binary(y_true, y_pred)
        if f1 > best_f1:
            best_f1 = f1
            best_t = float(t)
    return best_t

def evaluate_regression(pred: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
    pred = pred.reshape(-1).astype(float)
    y_true = y_true.reshape(-1).astype(float)
    return {
        "rmse": rmse(y_true, pred),
        "mae": mae(y_true, pred),
        "r2": r2(y_true, pred),
    }

def train_one(
    X_train: np.ndarray, y_train: np.ndarray,
    X_val: np.ndarray, y_val: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    problem_type: str,
    hidden: List[int],
    dropout: float,
    lr: float,
    weight_decay: float,
    max_epochs: int,
    patience: int,
    max_params: int,
    max_train_seconds: int,
    seed: int,
    device: str
) -> RunResult:
    set_seed(seed)
    start = time.time()
    notes: List[str] = []

    in_dim = X_train.shape[1]
    out_dim = 1

    model = SmallMLP(in_dim=in_dim, out_dim=out_dim, hidden=hidden, dropout=dropout).to(device)
    params = count_parameters(model)
    if params > max_params:
        raise ValueError(f"Model params {params} exceeds max_params {max_params}")

    criterion = nn.BCEWithLogitsLoss() if problem_type == "classification" else nn.MSELoss()
    opt = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    Xtr = torch.from_numpy(X_train).to(device)
    ytr = torch.from_numpy(y_train.reshape(-1, 1).astype(np.float32)).to(device)
    Xva = torch.from_numpy(X_val).to(device)
    yva = torch.from_numpy(y_val.reshape(-1, 1).astype(np.float32)).to(device)

    best_val, best_state, bad = None, None, 0
    for epoch in range(1, max_epochs + 1):
        if time.time() - start > max_train_seconds:
            notes.append("Stopped due to max_train_seconds.")
            break
        model.train()
        opt.zero_grad()
        loss = criterion(model(Xtr), ytr)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

        model.eval()
        with torch.no_grad():
            v_loss = float(criterion(model(Xva), yva).item())
        if (best_val is None) or (v_loss < best_val - 1e-6):
            best_val, best_state, bad = v_loss, {k: v.cpu().clone() for k, v in model.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= patience:
                notes.append("Early stopping triggered.")
                break

    if best_state: model.load_state_dict(best_state)

    def predict_np(X):
        model.eval()
        with torch.no_grad():
            return model(torch.from_numpy(X).to(device)).cpu().numpy()

    tr_out, va_out, te_out = predict_np(X_train), predict_np(X_val), predict_np(X_test)
    threshold, cm = None, None
    if problem_type == "classification":
        threshold = pick_threshold_for_f1(va_out, y_val)
        tr_eval = evaluate_classification(tr_out, y_train, threshold)
        va_eval = evaluate_classification(va_out, y_val, threshold)
        te_eval = evaluate_classification(te_out, y_test, threshold)
        tr_m, va_m, te_m, cm = tr_eval["metrics"], va_eval["metrics"], te_eval["metrics"], te_eval["cm"]
    else:
        tr_m, va_m, te_m = evaluate_regression(tr_out, y_train), evaluate_regression(va_out, y_val), evaluate_regression(te_out, y_test)

    return RunResult(
        architecture={"type": "SmallMLP", "in_dim": int(in_dim), "hidden": hidden, "dropout": float(dropout), "out_dim": 1},
        params_count=int(params),
        train_metrics=tr_m, val_metrics=va_m, test_metrics=te_m,
        threshold=threshold, confusion_matrix=cm, preprocess={}, notes=notes, state_dict=best_state
    )

def run_neurobuilder(spec: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.time()
    problem_type, seed = spec["problem_type"], int(spec.get("seed", 42))
    constraints = spec.get("constraints", {})
    max_params, max_train_sec = int(constraints.get("max_params", 50000)), int(constraints.get("max_train_seconds", 60))
    device = "cpu" if bool(constraints.get("cpu_only", True)) or not torch.cuda.is_available() else "cuda"

    if "dataset" in spec:
        df = pd.read_csv(spec["dataset"]) if spec["dataset"].endswith(".csv") else pd.read_parquet(spec["dataset"])
        target_col = spec["target_column"]
        df = df.dropna(subset=[target_col])
        if len(df) < 30: raise ValueError("Dataset too small.")
        pp = fit_preprocess(df, target_col, features=spec.get("features"), cat_topk=int(spec.get("cat_topk", 50)))
        X, y = transform(df, pp), df[target_col].values
        if problem_type == "classification":
            uniq = pd.unique(pd.Series(y).dropna())
            mapping = {uniq[0]: 0, uniq[1]: 1}
            y = np.array([mapping[v] for v in y], dtype=np.int64)
        else:
            y = pd.to_numeric(pd.Series(y), errors="coerce").values.astype(np.float32)
            mask = np.isfinite(y)
            X, y = X[mask], y[mask]
    else:
        X, y, pp = np.asarray(spec["X"], dtype=np.float32), np.asarray(spec["y"]), None

    (Xtr, ytr), (Xva, yva), (Xte, yte) = train_val_test_split(X, y, seed=seed)
    search = [{"hidden": [32, 16], "dropout": 0.1, "lr": 2e-3, "wd": 1e-4}, {"hidden": [64, 32], "dropout": 0.2, "lr": 2e-3, "wd": 1e-4}, {"hidden": [32], "dropout": 0.0, "lr": 1e-3, "wd": 0.0}]
    best, best_key, notes = None, None, []
    metric = spec.get("quality_goal", {}).get("metric", "f1" if problem_type == "classification" else "rmse")

    for i, cand in enumerate(search):
        if time.time() - t0 > max_train_sec: break
        try:
            res = train_one(Xtr, ytr, Xva, yva, Xte, yte, problem_type, cand["hidden"], cand["dropout"], cand["lr"], cand["wd"], 200, 15, max_params, max_train_sec - int(time.time()-t0), seed+i, device)
            score = -res.val_metrics[metric] if metric in ("rmse", "mae") else res.val_metrics[metric]
            if best is None or score > best_key: best, best_key = res, score
        except Exception as e: notes.append(f"Cand {i} failed: {str(e)}")

    if not best: raise RuntimeError("All candidates failed.")
    best.preprocess = asdict(pp) if pp else {}
    
    # Export
    export_cfg = spec.get("export", {"format": "json_weights", "path": "./model_artifact"})
    export_path = export_cfg["path"]
    os.makedirs(export_path, exist_ok=True)
    
    report = asdict(best)
    del report["state_dict"]
    report["preprocess_steps"] = list(best.preprocess.keys())
    
    if export_cfg["format"] == "json_weights":
        weights = {k: v.numpy().tolist() for k, v in best.state_dict.items()}
        with open(os.path.join(export_path, "model.json"), "w") as f:
            json.dump({"config": best.architecture, "weights": weights, "preprocess": best.preprocess}, f)
    elif export_cfg["format"] == "torchscript":
        m = SmallMLP(best.architecture["in_dim"], 1, best.architecture["hidden"], 0.0)
        m.load_state_dict(best.state_dict)
        torch.jit.script(m).save(os.path.join(export_path, "model.pt"))
        with open(os.path.join(export_path, "preprocess.json"), "w") as f: json.dump(best.preprocess, f)

    with open(os.path.join(export_path, "report.json"), "w") as f: json.dump(report, f)
    return report

if __name__ == "__main__":
    # Example usage for standalone testing
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            spec = json.load(f)
            print(json.dumps(run_neurobuilder(spec), indent=2))
