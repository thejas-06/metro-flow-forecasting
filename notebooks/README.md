# 🔬 Machine Learning Research & Experimentation Lifecycle
### End-to-End Modeling, Feature Engineering & MLOps Pipelines (Notebooks 01–06)

This directory documents the research, exploratory data analysis, algorithm benchmarking, deep learning sequence evaluation, and production pipeline serialization for the Namma Metro Passenger Flow Forecasting System.

---

## ⚡ Executive Summary & Research Findings

```
                                  DATA & MODELING LIFECYCLE
                                  
  [01_Data_Loading]   ──►  Ingest raw RTI turnstile records (Boarding & Exits)
         │
  [02_EDA]            ──►  Uncover diurnal twin-peaks (8–10 AM & 5–8 PM) & station hierarchies
         │
  [03_Preprocessing]  ──►  Engineer cyclical encodings, multi-scale lags & rolling volatility
         │
  [04_Model_Building] ──►  Benchmark Linear, Bagging & Gradient Boosting (XGBoost wins: R²=0.9701)
         │
  [05_Deep_Learning]  ──►  Evaluate Dense MLP, GRU & Stacked Bi-LSTM (Confirms tabular tree superiority)
         │
  [06_Production]     ──►  Package Scikit-Learn Pipeline object -> models/production_pipeline.joblib
```

### 📊 Model Benchmark Comparison

| Model Architecture | Category | RMSE | MAE | $R^2$ Score | System WMAPE | Production Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Ridge Regression** | Regularized Linear | `142.42` | `74.11` | `0.9107` | `19.32%` | Baseline |
| **Dense MLP** | Feed-Forward Neural Net | `130.54` | `81.46` | `0.9258` | `21.40%` | Baseline sequence |
| **Stacked Bi-LSTM** | Recurrent Neural Net | `113.46` | `60.57` | `0.9440` | `14.94%` | Sequence baseline |
| **Random Forest** | Bagging Ensemble | `83.70` | `41.81` | `0.9692` | `9.23%` | Non-linear baseline |
| **Tuned XGBoost** | Gradient Boosted Trees | `82.40` | `43.85` | `0.9701` | `8.77%` | **Production Selected** |
| **End-to-End Pipeline** | Unified Scikit-Learn + XGBoost | **`32.01`** | **`14.56`** | **`0.9955`** | **`4.08%`** | **🏆 Deployed Artifact** |

---

## 📂 Notebook Breakdown & Technical Specifications

### [01_Data_Loading_and_Understanding.ipynb](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/notebooks/01_Data_Loading_and_Understanding.ipynb)
* **Goal:** Ingest, inspect, and validate raw Right to Information (RTI) records from Bangalore Metro Rail Corporation (BMRCL).
* **Inputs:** `data/station-hourly.csv` (entry taps) & `data/station-hourly-exits.csv` (exit taps).
* **Key Tasks:**
  * Outer merge of entry/exit streams across 83 metro stations.
  * Schema alignment, null audit, and timestamp format consistency checks.
  * Verification of zero negative counts and data granularity (hourly intervals).

---

### [02_EDA.ipynb](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/notebooks/02_EDA.ipynb)
* **Goal:** Uncover spatial and temporal commuter dynamics across the transit network.
* **Key Discoveries:**
  * **Diurnal Twin Peaks:** Clear passenger spikes during Morning Rush (08:00–10:00) and Evening Surge (17:00–20:00).
  * **Station Cardinality & Hierarchy:** High-density transit hubs (e.g., Majestic Interchange, Indiranagar, MG Road) exhibit distinct high-volume patterns compared to residential peripheral stations.
  * **Weekend Dynamics:** Saturdays and Sundays show single, smooth afternoon leisure curves without sharp weekday commuter peaks.

---

### [03_Preprocessing_and_Feature_Engineering.ipynb](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/notebooks/03_Preprocessing_and_Feature_Engineering.ipynb)
* **Goal:** Transform raw temporal identifiers into rich mathematical feature representations.
* **Feature Engineering Strategy:**
  1. **Cyclical Encodings:** Transformed `Hour` and `DayOfWeek` using sine and cosine functions:
     $$\text{Hour\_Sin} = \sin\left(\frac{2\pi \cdot \text{Hour}}{24}\right), \quad \text{Hour\_Cos} = \cos\left(\frac{2\pi \cdot \text{Hour}}{24}\right)$$
  2. **Multi-Horizon Lags:** Created $t-1\text{h}$, $t-2\text{h}$, and seasonal $t-24\text{h}$ autoregressive features.
  3. **Rolling Volatility:** Computed 3-hour rolling mean and standard deviation to capture short-term crowd momentum.
* **Output:** `data/metro_processed.csv` (93,624 rows $\times$ 24 columns).

---

### [04_Model_Building.ipynb](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/notebooks/04_Model_Building.ipynb)
* **Goal:** Systematically evaluate and tune classical and ensemble Machine Learning models.
* **Methodology:**
  * Strict chronological train-test split (80/20) to prevent time-series lookahead bias.
  * Evaluated Ridge Regression (L2), Random Forest, and XGBoost Regressors.
  * Fine-tuned XGBoost using tree-depth bounds, subsampling, and learning rate scheduling.
* **Result:** XGBoost achieved the best balance of variance explanation ($R^2 = 0.9701$) and sub-50ms inference latency.

---

### [05_Deep_Learning_LSTM.ipynb](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/notebooks/05_Deep_Learning_LSTM.ipynb)
* **Goal:** Investigate deep recurrent neural network architectures (MLP, GRU, Stacked Bi-LSTM) for sequential crowd modeling.
* **Architectures Tested:**
  * Multi-Layer Perceptron baseline.
  * Gated Recurrent Unit (GRU) with dropout.
  * Stacked Bidirectional LSTM with learning rate annealing.
* **Key Finding:** While the Bi-LSTM achieved a solid $R^2 = 0.9440$, tree-based Gradient Boosting outperformed neural sequences on tabular tabular lag structures with significantly lower computational overhead.

---

### [06_Production_Pipeline_Building.ipynb](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/notebooks/06_Production_Pipeline_Building.ipynb)
* **Goal:** Package the entire data transformation and modeling lifecycle into a deployable Scikit-Learn `Pipeline`.
* **Custom Estimators Developed:**
  * `TemporalFeatureExtractor` (inherits `BaseEstimator`, `TransformerMixin`): Computes cyclical trigonometric values and rush-hour flags.
  * `StationBaselineEncoder`: Computes station volume priors with zero target leakage.
  * `LagAndRollingTransformer`: Handles cold-start nulls and multi-scale temporal lags.
  * `FeatureColumnSelector`: Guarantees deterministic 19-feature vector ordering.
* **Artifacts Generated:**
  * `models/production_pipeline.joblib`: Serialized end-to-end pipeline.
  * `models/pipeline_metadata.json`: Machine-readable metadata, versioning, and test scores.

---

## 🛠️ Execution & Reproducibility

To re-run any notebook from the project root:

```bash
# 1. Activate project virtual environment
# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate

# 2. Launch JupyterLab or Notebook server
jupyter lab notebooks/
```

All notebooks are pre-configured to load relative paths from either the `notebooks/` directory or root workspace.
