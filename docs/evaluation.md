# Evaluation

Let TP, FP, TN and FN denote confusion-matrix counts.

- Precision = TP / (TP + FP)
- Recall / Detection Rate = TP / (TP + FN)
- F1 = 2 × Precision × Recall / (Precision + Recall)
- False Discovery Rate (FDR) = FP / (TP + FP)
- False Negative Rate = FN / (TP + FN)
- False Positive Rate = FP / (FP + TN)

FDR is deliberately distinguished from false-positive rate.

## MTTD
Conceptually, MTTD is `detection_timestamp - anomaly_injection_timestamp`. In this batch emulation the injection event occurs before a detector batch executes, so the default benchmark records detector processing latency as a reproducible MTTD proxy. This must not be interpreted as real-time production MTTD. A real SAP/process-chain integration should persist injection/arrival and detection timestamps from the orchestration boundary.
