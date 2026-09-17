# Detection Methodology

## Rule based
A modular rule registry checks margin consistency, currency and master-data references, UoM semantics, temporal ordering, duplicates and exchange-rate plausibility.

## Statistical
Z-score and IQR detectors operate over engineered numeric semantic features. Rolling Z-score, rolling IQR, moving-average/standard-deviation deviation, percentile detection, and dynamic rolling-quantile thresholds are included for time-local experiments.

## Unsupervised ML
- Isolation Forest
- One-Class SVM
- Reconstruction autoencoder implemented with an `MLPRegressor` bottleneck network

The first 60% of observations are used as unsupervised training/calibration data. Labels are not supplied to model fitting. Robust scaling is fitted only on the training slice. The main threshold is a configurable quantile of training anomaly scores. Evaluation labels are joined only after prediction.

## Threshold calibration
`evaluation.threshold_sweep` supports post-hoc research analysis across score quantiles. Such sweeps may use labels to characterize the precision/recall/FDR trade-off, but they are not the model-training step and must be reported as evaluation-time calibration if used to select a final threshold.
