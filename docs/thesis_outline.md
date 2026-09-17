# Thesis Support Outline

## Chapter 1 — Introduction
Problem: technically valid warehouse records can be semantically wrong. Motivate semantic data quality, anomaly detection, LSA++ placement and performance trade-offs.

## Chapter 2 — Literature Review Structure
Data quality dimensions; enterprise data warehouses; anomaly-detection taxonomy; unsupervised methods; data-quality observability; SAP BW/4HANA/LSA++ architecture. **Do not insert citations until sources are verified.**

## Chapter 3 — Methodology
Synthetic controlled experiment, corruption engine, ground truth, unsupervised training, threshold strategy, metrics, repeated runs and reproducibility.

## Chapter 4 — System Architecture
TechNova O2C/Finance model, LSA++-style layers, detection engine, external-ML boundary.

## Chapter 5 — Experimental Design
Dataset-size × corruption-rate × detector × layer × seed matrix; performance instrumentation; hypotheses and statistical analysis plan.

## Chapter 6 — Results
Populate only from executed experiment result files. Include confidence intervals and per-corruption detection where measured.

## Chapter 7 — Discussion
Interpret effectiveness, placement and computational-overhead trade-offs without overstating synthetic evidence.

## Chapter 8 — Limitations and Future Work
Synthetic-to-production validity, actual SAP DTP validation, streaming/near-real-time variants, explainability improvements and operational governance.
