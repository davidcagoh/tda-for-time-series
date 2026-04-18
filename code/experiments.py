"""
experiments.py — Fixes three methodological issues in the TDA time-series study.

Issue 1: Multiple realizations per regime (5 realizations, mean ± std Wasserstein matrix)
Issue 2: k-NN classification accuracy on the 5×4=20 point clouds
Issue 3: Prediction experiment broken out by regime (4 separate MSE comparisons)
"""

import numpy as np
from scipy.integrate import odeint
from ripser import ripser
from persim import wasserstein
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# Synthesis helpers
# ─────────────────────────────────────────────────────────────────────────────

def synthesize_periodic(n, freq=1.0, dt=0.01, phase=0.0):
    t = np.arange(n) * dt
    return np.sin(2 * np.pi * freq * t + phase)


def synthesize_quasi_periodic(n, dt=0.01, phase=0.0):
    t = np.arange(n) * dt
    return (np.sin(2 * np.pi * np.sqrt(2) * t + phase)
            + 0.5 * np.sin(2 * np.pi * np.sqrt(3) * t + phase * 1.3))


def lorenz(state, t, sigma, rho, beta):
    x, y, z = state
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]


def synthesize_chaotic(n, dt=0.01, ic_seed=0):
    rng = np.random.default_rng(ic_seed)
    state0 = rng.uniform(-2, 2, 3)
    t = np.linspace(0, (n - 1) * dt, n)
    sol = odeint(lorenz, state0, t, args=(10.0, 28.0, 8/3))
    return sol[:, 0]


def synthesize_noise(n, seed=0):
    return np.random.default_rng(seed).standard_normal(n)


def delay_embed(x, m, tau):
    n = len(x)
    L = n - (m - 1) * tau
    return np.column_stack([x[i: i + L] for i in range(0, m * tau, tau)])


# ─────────────────────────────────────────────────────────────────────────────
# Generate 5 realizations per regime
# ─────────────────────────────────────────────────────────────────────────────

N_REALIZATIONS = 5
N = 2000
M, TAU = 3, 10
REGIMES = ["periodic", "quasi_periodic", "chaotic", "noise"]

PHASE_OFFSETS = [0.0, 0.3, 0.7, 1.2, 1.8]   # for periodic / quasi-periodic
NOISE_SEEDS   = [10, 20, 30, 40, 50]          # for noise realizations
LORENZ_SEEDS  = [0, 1, 2, 3, 4]              # for chaotic IC seeds

def get_realization(regime, k):
    """Return time series for regime, realization index k (0-based)."""
    if regime == "periodic":
        return synthesize_periodic(N, phase=PHASE_OFFSETS[k])
    elif regime == "quasi_periodic":
        return synthesize_quasi_periodic(N, phase=PHASE_OFFSETS[k])
    elif regime == "chaotic":
        return synthesize_chaotic(N, ic_seed=LORENZ_SEEDS[k])
    elif regime == "noise":
        return synthesize_noise(N, seed=NOISE_SEEDS[k])
    else:
        raise ValueError(regime)


def get_h1(X, subsample=500, seed=0):
    """Compute H1 persistence diagram, subsampling for speed."""
    if len(X) > subsample:
        idx = np.random.default_rng(seed).choice(len(X), subsample, replace=False)
        X = X[idx]
    dgms = ripser(X, maxdim=1)["dgms"]
    h1 = dgms[1]
    return h1[np.isfinite(h1[:, 1])] if len(h1) > 0 else np.zeros((0, 2))


print("=" * 60)
print("Computing H1 diagrams for 5 realizations × 4 regimes …")
print("=" * 60)

# diagrams[regime][k] = H1 diagram
diagrams = {r: [] for r in REGIMES}
for regime in REGIMES:
    for k in range(N_REALIZATIONS):
        ts = get_realization(regime, k)
        X = delay_embed(ts, M, TAU)
        h1 = get_h1(X, subsample=500, seed=k)
        diagrams[regime].append(h1)
        print(f"  {regime}[{k}]: {len(h1)} H1 bars")

# ─────────────────────────────────────────────────────────────────────────────
# ISSUE 1 — 4×4 Wasserstein matrix with mean ± std
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Issue 1: Wasserstein distance matrix (mean ± std)")
print("=" * 60)

# For each pair of regimes, compute all 5×5=25 pairwise distances
# then report mean ± std across the 25 pairs.
W_mean = np.zeros((4, 4))
W_std  = np.zeros((4, 4))

for i, r1 in enumerate(REGIMES):
    for j, r2 in enumerate(REGIMES):
        if i == j:
            W_mean[i, j] = 0.0
            W_std[i, j]  = 0.0
            continue
        dists = []
        for k1 in range(N_REALIZATIONS):
            for k2 in range(N_REALIZATIONS):
                d1, d2 = diagrams[r1][k1], diagrams[r2][k2]
                if len(d1) == 0 or len(d2) == 0:
                    dists.append(np.nan)
                else:
                    dists.append(wasserstein(d1, d2))
        dists = np.array(dists)
        W_mean[i, j] = np.nanmean(dists)
        W_std[i, j]  = np.nanstd(dists)

# Print the table
header = " " * 18 + "  ".join(f"{r:>15}" for r in REGIMES)
print(header)
for i, r1 in enumerate(REGIMES):
    row = f"{r1:>18}  "
    for j in range(4):
        if i == j:
            row += f"{'0.00 ± 0.00':>15}  "
        else:
            row += f"{W_mean[i,j]:.2f} ± {W_std[i,j]:.2f}".rjust(15) + "  "
    print(row)

# Save a figure
fig, ax = plt.subplots(figsize=(8, 6))
labels = [r.replace("_", "\n") for r in REGIMES]
im = ax.imshow(W_mean, cmap="viridis_r")
ax.set_xticks(range(4)); ax.set_xticklabels(labels, fontsize=9)
ax.set_yticks(range(4)); ax.set_yticklabels(labels, fontsize=9)
for i in range(4):
    for j in range(4):
        ax.text(j, i, f"{W_mean[i,j]:.1f}\n±{W_std[i,j]:.1f}",
                ha="center", va="center", fontsize=7,
                color="white" if W_mean[i,j] > W_mean.max()/2 else "black")
plt.colorbar(im, ax=ax, label="Wasserstein distance")
ax.set_title("H1 Wasserstein distance matrix\nmean ± std across 5 realizations per regime")
plt.tight_layout()
plt.savefig(
    "/Users/davidgoh/LocalFiles/2025-26-Ongoing/meta-priors/tda-for-time-series/wasserstein_matrix.png",
    dpi=150
)
plt.close()
print("\nSaved wasserstein_matrix.png")

# ─────────────────────────────────────────────────────────────────────────────
# ISSUE 2 — k-NN (k=1) leave-one-out classification on 20 diagrams
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Issue 2: LOO k-NN (k=1) classification")
print("=" * 60)

# Build flat list of 20 diagrams with labels
all_diagrams = []
all_labels   = []
for r in REGIMES:
    for k in range(N_REALIZATIONS):
        all_diagrams.append(diagrams[r][k])
        all_labels.append(r)

n_total = len(all_diagrams)

# Pre-compute full 20×20 Wasserstein distance matrix
print(f"Building {n_total}×{n_total} pairwise distance matrix …")
D = np.zeros((n_total, n_total))
for i in range(n_total):
    for j in range(i + 1, n_total):
        d1, d2 = all_diagrams[i], all_diagrams[j]
        if len(d1) == 0 or len(d2) == 0:
            w = np.nan
        else:
            w = wasserstein(d1, d2)
        D[i, j] = w
        D[j, i] = w

# LOO k=1 NN
predictions = []
for i in range(n_total):
    row = D[i].copy()
    row[i] = np.inf  # exclude self
    nn_idx = np.argmin(row)
    predictions.append(all_labels[nn_idx])

# Accuracy
correct = sum(p == t for p, t in zip(predictions, all_labels))
overall_acc = correct / n_total
print(f"\nOverall LOO k-NN accuracy: {correct}/{n_total} = {overall_acc:.1%}")

# Per-class accuracy
print("\nPer-class accuracy:")
for r in REGIMES:
    idxs = [i for i, l in enumerate(all_labels) if l == r]
    c = sum(predictions[i] == r for i in idxs)
    print(f"  {r:>18}: {c}/{len(idxs)} = {c/len(idxs):.1%}")

# Confusion matrix
print("\nConfusion matrix (rows=true, cols=predicted):")
print(f"{'':>18}  " + "  ".join(f"{r[:6]:>8}" for r in REGIMES))
confusion = np.zeros((4, 4), dtype=int)
for true_label, pred_label in zip(all_labels, predictions):
    i = REGIMES.index(true_label)
    j = REGIMES.index(pred_label)
    confusion[i, j] += 1

for i, r in enumerate(REGIMES):
    print(f"  {r:>18}  " + "  ".join(f"{confusion[i,j]:>8}" for j in range(4)))

# Save confusion matrix figure
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(confusion, cmap="Blues")
short = [r.replace("_", "\n") for r in REGIMES]
ax.set_xticks(range(4)); ax.set_xticklabels(short, fontsize=9)
ax.set_yticks(range(4)); ax.set_yticklabels(short, fontsize=9)
ax.set_xlabel("Predicted"); ax.set_ylabel("True")
for i in range(4):
    for j in range(4):
        ax.text(j, i, str(confusion[i, j]),
                ha="center", va="center", fontsize=12,
                color="white" if confusion[i, j] > 2 else "black")
ax.set_title(f"LOO k-NN Confusion Matrix (k=1)\nOverall accuracy: {overall_acc:.1%}")
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig(
    "/Users/davidgoh/LocalFiles/2025-26-Ongoing/meta-priors/tda-for-time-series/classification_results.png",
    dpi=150
)
plt.close()
print("\nSaved classification_results.png")

# ─────────────────────────────────────────────────────────────────────────────
# ISSUE 3 — Prediction experiment per regime
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Issue 3: Prediction experiment per regime")
print("=" * 60)

L_WIN = 50
M_WIN, TAU_WIN = 3, 5


def delay_embed_window(x, m, tau):
    n_pts = len(x) - (m - 1) * tau
    if n_pts <= 0:
        return np.zeros((0, m))
    return np.column_stack([x[i: i + n_pts] for i in range(0, m * tau, tau)])


def ph_basic(window, m, tau):
    X = delay_embed_window(window, m, tau)
    if len(X) < 4:
        return np.zeros(4)
    dgms = ripser(X, maxdim=1)["dgms"]
    h1 = dgms[1]
    h1 = h1[np.isfinite(h1[:, 1])]
    if len(h1) == 0:
        return np.zeros(4)
    pers = h1[:, 1] - h1[:, 0]
    return np.array([pers.mean(), pers.max(), float(len(pers)),
                     pers.std() if len(pers) > 1 else 0.0])


def run_prediction_for_regime(regime):
    """Run the sliding-window prediction experiment for a single regime.
    Uses a single canonical realization (realization 0 / baseline seed).
    Returns (mse_raw, mse_ph).
    """
    # Use baseline realization for prediction experiment
    ts = get_realization(regime, 0)
    split = int(len(ts) * 0.8)

    # Build train windows
    X_raw_tr, X_ph_tr, y_tr = [], [], []
    for i in range(split - L_WIN):
        w = ts[i: i + L_WIN]
        X_raw_tr.append(w)
        X_ph_tr.append(ph_basic(w, M_WIN, TAU_WIN))
        y_tr.append(ts[i + L_WIN])

    # Build test windows
    X_raw_te, X_ph_te, y_te = [], [], []
    for i in range(split, len(ts) - L_WIN):
        w = ts[i: i + L_WIN]
        X_raw_te.append(w)
        X_ph_te.append(ph_basic(w, M_WIN, TAU_WIN))
        y_te.append(ts[i + L_WIN])

    X_raw_tr = np.array(X_raw_tr)
    X_raw_te = np.array(X_raw_te)
    X_ph_tr  = np.array(X_ph_tr)
    X_ph_te  = np.array(X_ph_te)
    y_tr = np.array(y_tr)
    y_te = np.array(y_te)

    X_comb_tr = np.hstack([X_raw_tr, X_ph_tr])
    X_comb_te = np.hstack([X_raw_te, X_ph_te])

    scaler_r = StandardScaler().fit(X_raw_tr)
    scaler_c = StandardScaler().fit(X_comb_tr)

    lm_r = LinearRegression().fit(scaler_r.transform(X_raw_tr), y_tr)
    lm_c = LinearRegression().fit(scaler_c.transform(X_comb_tr), y_tr)

    mse_r = mean_squared_error(y_te, lm_r.predict(scaler_r.transform(X_raw_te)))
    mse_c = mean_squared_error(y_te, lm_c.predict(scaler_c.transform(X_comb_te)))

    return mse_r, mse_c


pred_results = {}
for regime in REGIMES:
    print(f"  Running prediction for {regime} …", flush=True)
    mse_r, mse_c = run_prediction_for_regime(regime)
    pred_results[regime] = (mse_r, mse_c)
    delta = (mse_c - mse_r) / mse_r * 100
    print(f"    MSE raw={mse_r:.4f}  MSE+PH={mse_c:.4f}  Δ={delta:+.2f}%")

print("\nPrediction table:")
print(f"{'Regime':>18} | {'MSE (raw)':>12} | {'MSE (raw+PH)':>14} | {'Δ%':>8}")
print("-" * 60)
for regime in REGIMES:
    mse_r, mse_c = pred_results[regime]
    delta = (mse_c - mse_r) / mse_r * 100
    print(f"{regime:>18} | {mse_r:>12.4f} | {mse_c:>14.4f} | {delta:>+8.2f}%")

# Save prediction figure
fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(REGIMES))
mse_raw_vals = [pred_results[r][0] for r in REGIMES]
mse_ph_vals  = [pred_results[r][1] for r in REGIMES]
width = 0.35
bars1 = ax.bar(x - width/2, mse_raw_vals, width, label="Raw window", color="steelblue")
bars2 = ax.bar(x + width/2, mse_ph_vals,  width, label="Raw + PH",   color="darkorange")
ax.set_xticks(x)
ax.set_xticklabels([r.replace("_", "\n") for r in REGIMES], fontsize=9)
ax.set_ylabel("MSE (next-step prediction)")
ax.set_title("Prediction MSE per regime: raw window vs. raw + PH features\n(L=50, m=3, τ=5, 80/20 temporal split, LinearRegression)")
ax.legend()
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
            f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=7)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
            f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=7)
plt.tight_layout()
plt.savefig(
    "/Users/davidgoh/LocalFiles/2025-26-Ongoing/meta-priors/tda-for-time-series/prediction_by_regime.png",
    dpi=150
)
plt.close()
print("\nSaved prediction_by_regime.png")

# ─────────────────────────────────────────────────────────────────────────────
# Print all result numbers in one place for REPORT.md
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("SUMMARY FOR REPORT.md")
print("=" * 60)

print("\n--- Result 1: Wasserstein matrix (mean ± std) ---")
print(f"{'':>20}", end="")
for r in REGIMES:
    print(f"  {r:>22}", end="")
print()
for i, r1 in enumerate(REGIMES):
    print(f"{r1:>20}", end="")
    for j in range(4):
        if i == j:
            cell = "0.00 ± 0.00"
        else:
            cell = f"{W_mean[i,j]:.2f} ± {W_std[i,j]:.2f}"
        print(f"  {cell:>22}", end="")
    print()

print("\n--- Result 1b: k-NN Classification ---")
print(f"Overall accuracy: {overall_acc:.1%} ({correct}/{n_total})")
for r in REGIMES:
    idxs = [i for i, l in enumerate(all_labels) if l == r]
    c = sum(predictions[i] == r for i in idxs)
    print(f"  {r:>18}: {c/len(idxs):.1%}")
print("\nConfusion matrix:")
print(f"{'':>20}", end="")
for r in REGIMES:
    print(f"  {r[:8]:>10}", end="")
print()
for i, r in enumerate(REGIMES):
    print(f"{r:>20}", end="")
    for j in range(4):
        print(f"  {confusion[i,j]:>10}", end="")
    print()

print("\n--- Result 3: Prediction per regime ---")
print(f"{'Regime':>18} | {'MSE raw':>10} | {'MSE+PH':>10} | {'Δ%':>8}")
print("-" * 55)
for regime in REGIMES:
    mse_r, mse_c = pred_results[regime]
    delta = (mse_c - mse_r) / mse_r * 100
    print(f"{regime:>18} | {mse_r:>10.4f} | {mse_c:>10.4f} | {delta:>+8.2f}%")
