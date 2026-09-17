# Measured Smoke-Test Results

These values were **actually measured** on the local execution environment on 17 September 2026. They are a single reproducibility smoke test, not a statistically sufficient answer to RQ1–RQ3.

- Configuration: `config/small.yaml`
- Random seed: 42
- Requested sales orders: 800
- Resulting semantic records: 2,307
- Configured anomaly rate: 2%
- Logged corruption events: 46
- Record-level positives after phantom-delta pair labelling: 51
- Architectural status: **SAP BW/4HANA architectural emulation**
- Performance status: **DTP-like local batch simulation**, not SAP DTP measurement

| layer         | detector         |   precision |   recall |    f1 |   fdr |   runtime_seconds |   throughput |
|:--------------|:-----------------|------------:|---------:|------:|------:|------------------:|-------------:|
| inbound       | baseline         |       0     |    0     | 0     | 0     |            0.0008 |    2,838,068 |
| inbound       | rules            |       0.938 |    0.588 | 0.723 | 0.062 |            0.1536 |       15,015 |
| inbound       | zscore           |       0.079 |    0.157 | 0.105 | 0.921 |            0.0196 |      117,816 |
| inbound       | iqr              |       0.049 |    0.196 | 0.078 | 0.951 |            0.0226 |      101,878 |
| inbound       | isolation_forest |       0     |    0     | 0     | 1     |            0.1436 |       16,063 |
| inbound       | one_class_svm    |       0.138 |    0.157 | 0.147 | 0.862 |            0.0197 |      117,192 |
| inbound       | autoencoder      |       0.188 |    0.176 | 0.182 | 0.812 |            0.2093 |       11,021 |
| harmonization | baseline         |       0     |    0     | 0     | 0     |            0.0004 |    5,204,820 |
| harmonization | rules            |       0.938 |    0.588 | 0.723 | 0.062 |            0.1395 |       16,533 |
| harmonization | zscore           |       0.078 |    0.157 | 0.105 | 0.922 |            0.014  |      164,555 |
| harmonization | iqr              |       0.049 |    0.196 | 0.078 | 0.951 |            0.0243 |       95,086 |
| harmonization | isolation_forest |       0     |    0     | 0     | 1     |            0.1395 |       16,542 |
| harmonization | one_class_svm    |       0.073 |    0.118 | 0.09  | 0.927 |            0.0225 |      102,690 |
| harmonization | autoencoder      |       0.196 |    0.176 | 0.186 | 0.804 |            0.2275 |       10,142 |

## Interpretation guardrails

The rule engine performs strongly in this smoke test because several injected corruptions deliberately correspond to deterministic semantic constraints. The unsupervised models use a generic threshold and one small synthetic run; their scores must not be treated as conclusions about model superiority or architectural placement. The full multi-seed size × corruption-rate matrix and statistical analysis are required before research conclusions are made.
