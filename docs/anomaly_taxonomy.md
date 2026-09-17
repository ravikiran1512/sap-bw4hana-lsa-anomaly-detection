# Anomaly Taxonomy

The controlled corruption engine injects and logs nine categories: numeric drift, margin corruption, exchange-rate drift, UoM corruption, currency mismatch, phantom delta, referential-integrity corruption, temporal corruption, and collective anomalies.

Every injection writes an anomaly identifier, type, affected record and fields, UTC timestamp, severity, ground-truth label, source layer, human-readable description and injection method. The separate record-level ground-truth file includes normal records too, enabling objective evaluation.
