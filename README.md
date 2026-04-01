# tda-for-time-series

**tda-for-time-series** is a notebook-centered research project that uses **topological data analysis (TDA)** to compare the geometry of different time-series regimes. The core workflow is to convert a scalar series into a delay embedding, compute persistent homology on the resulting point cloud, and then compare regimes such as periodic, quasi-periodic, chaotic, and noisy dynamics through both visualization and distance-based summaries.

The repository is best read as an exploratory technical study rather than a packaged library. Its value is in showing how topological structure can be extracted from time-series data and used as an interpretable lens on dynamical behavior.

| Repository focus | Description |
|---|---|
| Research domain | Topological data analysis for dynamical systems and time series |
| Core pipeline | Delay embedding → persistent homology → visual and quantitative comparison |
| Canonical regimes | Periodic, quasi-periodic, chaotic, and stochastic signals |
| Main outputs | Persistence diagrams, Betti curves, persistence images, and Wasserstein comparisons |
| Portfolio value | Shows mathematical modeling, experimental workflow design, and scientific computing in one project |

## What this project does

The project starts from a simple question: if two time series behave differently as dynamical systems, can that difference be seen not only in the time domain, but also in the **shape** of their reconstructed state spaces? Delay embeddings provide a geometric representation of a one-dimensional series, and persistent homology then measures which topological features of that geometry persist across scales.

This makes the repository a compact example of applied mathematical experimentation. Rather than treating TDA as an abstract method, it uses it to compare concrete signal classes and to ask whether topology provides a meaningful summary of regime differences.

| Stage | Purpose |
|---|---|
| Data generation / loading | Create or import representative time series |
| Delay embedding | Turn each scalar series into a point cloud in \(\mathbb{R}^m\) |
| Persistent homology | Compute topological summaries, especially in \(H_1\) |
| Visualization | Inspect persistence diagrams, images, and Betti curves |
| Quantitative comparison | Measure regime similarity via Wasserstein distance |

## Main analytical workflow

The implemented notebook focuses on four canonical regimes. Periodic and quasi-periodic signals produce structured embeddings with more obvious loop-like geometry, while chaotic and noisy series typically generate more diffuse point clouds and shorter-lived topological features. The repository uses that contrast to study which summaries are visually and numerically informative.

| Regime | Intended role in the analysis |
|---|---|
| Periodic | Baseline with strong recurring structure |
| Quasi-periodic | Structured but richer than a single clean cycle |
| Chaotic | Deterministic but irregular dynamics |
| Noise | Unstructured stochastic comparison point |

## Core outputs

The project combines descriptive and quantitative analysis rather than relying on a single visualization.

| Output | Interpretation |
|---|---|
| Persistence diagrams | Show birth and death of topological features across scales |
| Betti curves | Summarize the number of active features as filtration scale changes |
| Persistence images | Vectorize diagram structure for easier comparison |
| Wasserstein distance matrix | Quantifies dissimilarity between regimes in diagram space |

These outputs make the repository useful as both a research note and a portfolio piece. A reader can see the full pipeline from signal generation to interpretable summaries and regime comparison.

## Running the project

The main work lives in the notebook, which should be executed top to bottom after installing the required scientific Python packages.

```bash
pip install numpy scipy matplotlib pandas seaborn ripser persim scikit-learn
```

Once the environment is ready, open the notebook and run the cells sequentially so that embeddings, diagrams, and derived visualizations remain consistent.

## Key configuration choices

The main experimental parameters are the time-series length `n`, embedding dimension `m`, and delay `tau`. These determine the geometry of the reconstructed point cloud and strongly affect both runtime and interpretability.

| Parameter | Role |
|---|---|
| `n` | Number of samples in the time series |
| `m` | Embedding dimension for the delay-coordinate reconstruction |
| `tau` | Lag between coordinates in the embedding |
| `seed` | Reproducibility for stochastic or noisy regimes |

A practical constraint is that the embedding requires \(n > (m-1)\tau\). In addition, large embeddings can make Vietoris–Rips computations expensive, so subsampling or approximate strategies may be helpful when scaling beyond the current notebook experiments.

## How to extend it

The repository is structured so that new regimes or new topological summaries can be added without changing the overall logic of the workflow. To extend the analysis, add another time series, embed it with the same parameters, compute its persistence diagrams, and include it in the visualization and distance-comparison stages.

| Extension direction | Example |
|---|---|
| New dynamical regime | Real-world sensor series, market series, or biological oscillations |
| New summary type | Persistence landscapes, summary statistics, or alternative Betti-derived features |
| Predictive experiments | Sliding-window forecasting with PH-derived features |
| Alternative metrics | Compare diagrams with bottleneck or other stable distances |

## Reading this repository as a portfolio piece

From a portfolio perspective, **tda-for-time-series** demonstrates the ability to take a mathematically sophisticated method and turn it into a reproducible experimental workflow. It combines scientific computing, visualization, and conceptual clarity: the reader can follow not only what was computed, but also why the topology of the reconstructed state space is relevant in the first place.

The repository therefore works well as an example of technical research prototyping, especially for audiences interested in TDA, nonlinear dynamics, and data-driven mathematical analysis.
