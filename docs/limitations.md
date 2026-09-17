# Limitations

- Data is synthetic and cannot establish production generalizability by itself.
- Python/file execution emulates LSA++ placement; it is not an actual BW/4HANA deployment.
- DTP-like performance is a local batch simulation, not SAP DTP runtime.
- Memory is measured as process RSS delta and may understate peak memory.
- CPU usage is derived from process CPU time over wall time and can exceed 100% on multicore workloads.
- The lightweight autoencoder uses scikit-learn MLP reconstruction rather than a deep-learning framework, intentionally reducing dependencies.
- Threshold quantiles are configuration parameters. Threshold sweeps must be reported transparently to avoid evaluation leakage.
- Ground-truth corruption patterns are known by construction and may not represent all enterprise semantic errors.
- External SAP/ML integration security and operations are documented conceptually but not production-certified.
