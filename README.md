# Persistent Homology on Delay Embeddings of Time Series

## Purpose

This project implements a reproducible workflow for exploring **persistent homology (PH)** on **delay embeddings** of time series. The goal is to compare the topological structure of different dynamical regimes—periodic, quasi-periodic, chaotic, and purely stochastic—by turning each scalar series into a point cloud via delay embedding and then computing PH (Vietoris–Rips) on that point cloud. The notebook supports both **descriptive** analysis (visualization of persistence diagrams, Betti curves, persistence images) and **quantitative** comparison (pairwise Wasserstein distances between H1 diagrams). Optional predictive experiments use PH-derived features in a sliding-window regression setting. The documentation and code are intended for researchers and developers familiar with Python, topological data analysis (TDA), and time series who want to run, interpret, and extend the pipeline.

---

## Pipeline Overview

The workflow is organized into stages. Each stage has a clear goal, defined inputs and outputs, and feeds the next. Stages 0–4 are implemented in the main notebook; Stages 5 and 6 are outlined for future work.

---

### Stage 0 — Setup

**Goal**  
Install and import dependencies, and define global parameters (embedding dimension `m`, delay `tau`, series length `n`) so that all downstream stages use a consistent configuration.

**Inputs**  
- None (configuration is set in code or via parameters).

**Outputs**  
- Loaded libraries (e.g. NumPy, SciPy, `ripser`, `persim`, Matplotlib, Pandas, Seaborn).
- Resolved parameters: `n`, `m`, `tau`, and optionally `dt`, `noise_scale`, `seed`.

**Key instructions or tips**  
- Ensure `ripser` and `persim` (and optionally `scikit-learn` for scaling/regression in experiments) are installed.
- Run this cell first; later stages assume these imports and parameters exist. For reproducibility, fix `seed` when using stochastic series (noise, and optionally chaotic).

---

### Stage 1 — Data & Delay Embedding

**Goal**  
Generate or load time series and convert each into a delay-coordinate embedding: a point cloud in \(\mathbb{R}^m\) where each point is \((x(t), x(t-\tau), \ldots, x(t-(m-1)\tau))\). This stage produces the primary geometric objects on which PH will be computed.

**Inputs**  
- Parameters: series length `n`, embedding dimension `m`, delay `tau`, and (for synthetic data) `dt`, `noise_scale`, `seed`.
- Optional: user-provided time series instead of synthetic data.

**Outputs**  
- A dictionary of embeddings, e.g. keys `'periodic'`, `'quasi_periodic'`, `'chaotic'`, `'noise'`, each value a 2D array of shape `(L, m)` with \(L = n - (m-1)\tau\).
- The four canonical regimes: (1) **periodic** — single sinusoid; (2) **quasi-periodic** — sum of incommensurate frequencies; (3) **chaotic** — \(x(t)\) from the Lorenz system; (4) **noise** — white Gaussian noise.

**Notes**  
- Ensure \(n > (m-1)\tau\) so that the embedding is non-empty. Adjust `m` and `tau` to balance resolution and computational cost; typical starting values are \(m=3\), \(\tau\) on the order of 10–50 samples.
- For custom series, use the same `delay_embed` logic: stack lagged copies with step `tau` into columns. Normalize or standardize if comparing across different scales.

---

### Stage 2 — Persistent Homology

**Goal**  
Compute persistent homology (Vietoris–Rips) on each delay embedding up to dimension 1, and optionally derive vectorized summaries (e.g. persistence images) for downstream use. The focus is on **H1** (one-dimensional cycles), which captures loop-like structure in the embedding.

**Inputs**  
- The embeddings dictionary from Stage 1 (each entry a point cloud of shape `(L, m)`).
- PH options: maximum dimension (e.g. 1 for H0 and H1), and for persistence images: pixel size and fit range.

**Outputs**  
- For each regime: persistence diagrams (H0, H1) from `ripser`; optionally H1 persistence images from `persim.PersistenceImager`.
- In-memory structures (e.g. lists or dicts of diagrams and images) consumed by visualization and comparison stages.

**Notes**  
- Filter out infinite death values (e.g. H0 or H1 points with `death == np.inf`) before plotting or distance computations. Use finite bars only for persistence images and Wasserstein distances.
- For large point clouds, consider subsampling or using approximate Rips filtrations to control runtime. Persistence image resolution (`pixel_size`) trades off granularity and smoothness.

---

### Stage 3 — Descriptive Visualization

**Goal**  
Produce human-interpretable figures that summarize, for each dynamical regime, the delay embedding’s topology: persistence image, H1 persistence diagram, and H1 Betti curve. This supports qualitative comparison across regimes.

**Inputs**  
- Embeddings and PH outputs from Stages 1 and 2: diagrams (H1), persistence images, and (if not computed in Stage 2) Betti curves derived from H1.

**Outputs**  
- A multi-panel figure (e.g. one row per regime, columns: persistence image, H1 diagram, H1 Betti curve), with clear titles and axis labels.
- Optional: time-series or embedding previews if desired for context.

**Expectations**  
- Interpret short bars as noise or fine-scale structure; long bars as robust topological features (e.g. dominant cycles). Chaotic and noise regimes often show many short H1 bars; periodic and quasi-periodic regimes can show fewer, longer bars.

---

### Stage 4 — Quantitative Comparison

**Goal**  
Quantify pairwise dissimilarity between regimes using a stable metric on persistence diagrams. The notebook uses **Wasserstein distance** (or related metrics) on H1 diagrams to build a distance matrix and visualize it (e.g. heatmap).

**Inputs**  
- H1 persistence diagrams for each regime (finite bars only), as produced in Stage 2.

**Outputs**  
- Pairwise distance matrix (e.g. \(4 \times 4\) for the four canonical regimes).
- Heatmap or table summarizing distances; optional embedding (e.g. MDS) of regimes in “diagram space” for low-dimensional visualization.

**Notes**  
- Expect periodic and quasi-periodic to be relatively close, and noise to be farther from structured regimes; chaotic may sit between. Use the heatmap to check that distances match intuition before drawing conclusions.

---

### Stage 5 — Optional Prediction Experiment

**Goal**  
*(Future work.)* Use PH-derived features in a **predictive** setting: e.g. sliding windows over time series, compute PH summaries (e.g. basic stats, persistence landscapes, or Betti curves) per window, and train a simple model (e.g. linear regression) to predict the next value or a target. Compare performance with and without PH features to assess their added value.

**Inputs**  
- Time series (or embeddings) from Stage 1; window length \(L\); PH summary type (e.g. basic, landscape, Betti); train/test split (e.g. temporal 80/20).

**Outputs**  
- Feature matrices (raw windows and/or PH summaries), train/test splits, fitted model, and evaluation metrics (e.g. MSE, MAE).
- Comparison of metrics: model using only raw windows vs. model using raw windows plus PH features.

**Notes**  
- Use a **temporal** split to avoid leakage. Consider multiple PH summary types (basic, landscape, Betti) and window lengths. Scale features (e.g. StandardScaler) before regression. Document which summary and window size were used when reporting results.

---

### Stage 6 — Narrative / Summary

**Goal**  
*(Future work.)* Synthesize results into a short narrative: how topology differs across regimes, how well Wasserstein distances align with dynamical class, and whether PH features improve prediction. Provide takeaway bullets and suggestions for follow-up (e.g. other metrics, other embeddings, real data).

**Inputs**  
- Outputs and figures from Stages 3 and 4, and optionally from Stage 5.

**Outputs**  
- A concise written summary (in the notebook or a separate document) and, if desired, a final “summary” figure or table.

---

## Execution Notes for Users

- **Run order:** Execute cells in sequence from top to bottom. Stage 0 (imports and parameters) must run first; Stages 1–4 depend on previous stages. If you use optional experiment code (e.g. from `experiment.py`), ensure the notebook has already produced `embeddings` and that any shared parameters (`m`, `tau`, `n`, window length) are consistent.
- **Environment:** Use a Python environment with NumPy, SciPy, Matplotlib, Pandas, Seaborn, `ripser`, and `persim`. For prediction experiments, add `scikit-learn`. There is no `requirements.txt` in the repo; create one from your environment (e.g. `pip freeze`) if you need to reproduce the setup.
- **Extending the notebook:** To add a new regime, (1) synthesize or load the series, (2) run it through the same `delay_embed` with the same `m` and `tau`, (3) add the embedding to the dictionary, (4) run PH and append results to the diagram/image structures, and (5) extend the visualization and distance matrix to include the new row/column. For new PH summaries or metrics, add functions that take diagrams (or embeddings) and return vectors or scalars, then plug them into the comparison or prediction pipeline.
- **Visualizations:** All main figures are produced by the notebook (4×4 panel plot, Wasserstein heatmap). Save figures explicitly (e.g. `plt.savefig`) if you need them for reports or papers. Adjust `figsize`, DPI, and font sizes in the plotting cells to match your output format.
- **Interpretation:** Use persistence diagrams and Betti curves to judge “how much” 1-cycle structure each regime has; use Wasserstein distances to rank regimes by topological similarity. Short persistence bars typically indicate noise or unstable features; long bars indicate robust cycles. Chaotic and noise regimes often yield many short H1 bars; periodic and quasi-periodic regimes can yield fewer, longer bars consistent with dominant periods or tori.
- **Reproducibility:** Set random seeds for noise and, if applicable, for train/test splits in prediction experiments. Record versions of `ripser`, `persim`, and Python so that results can be recreated later.
