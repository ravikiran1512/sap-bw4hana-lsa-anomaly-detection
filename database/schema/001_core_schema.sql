-- PostgreSQL-compatible research schema. These are NOT SAP BW/4HANA objects.
CREATE TABLE IF NOT EXISTS anomaly_ground_truth (
  anomaly_id VARCHAR(32) PRIMARY KEY,
  anomaly_type VARCHAR(64) NOT NULL,
  affected_record VARCHAR(64) NOT NULL,
  affected_fields TEXT,
  injection_timestamp TIMESTAMP WITH TIME ZONE,
  severity VARCHAR(16),
  ground_truth_label SMALLINT NOT NULL,
  source_layer VARCHAR(32),
  corruption_description TEXT,
  injection_method VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS anomaly_result (
  anomaly_result_id VARCHAR(64) PRIMARY KEY,
  record_id VARCHAR(64) NOT NULL,
  layer VARCHAR(32) NOT NULL,
  detector_type VARCHAR(32) NOT NULL,
  detector_name VARCHAR(64) NOT NULL,
  anomaly_type VARCHAR(64),
  anomaly_score DOUBLE PRECISION,
  threshold DOUBLE PRECISION,
  prediction SMALLINT NOT NULL,
  ground_truth SMALLINT,
  detection_timestamp TIMESTAMP WITH TIME ZONE,
  processing_timestamp TIMESTAMP WITH TIME ZONE,
  severity VARCHAR(16),
  explanation TEXT
);

CREATE TABLE IF NOT EXISTS experiment_result (
  experiment_id VARCHAR(64), run_timestamp TIMESTAMP WITH TIME ZONE,
  dataset_size BIGINT, anomaly_rate DOUBLE PRECISION, layer VARCHAR(32), detector VARCHAR(64), model_version VARCHAR(32),
  precision DOUBLE PRECISION, recall DOUBLE PRECISION, f1 DOUBLE PRECISION, fdr DOUBLE PRECISION,
  mttd DOUBLE PRECISION, runtime_seconds DOUBLE PRECISION, memory_mb DOUBLE PRECISION, cpu_usage DOUBLE PRECISION,
  records_processed BIGINT, throughput DOUBLE PRECISION
);
