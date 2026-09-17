from pathlib import Path
from tn_anomaly.config import load_config
from tn_anomaly.pipeline import run_experiment

def test_pipeline_smoke(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg=load_config(Path(__file__).resolve().parents[1] / "config" / "small.yaml")
    cfg["data"]["sales_orders"]=80
    cfg["experiment"]["detectors"]=["rules","zscore","isolation_forest"]
    cfg["experiment"]["layers"]=["inbound"]
    cfg["experiment"]["output_dir"]="experiments/results"; cfg["experiment"]["run_dir"]="experiments/runs"
    r=run_experiment(cfg,persist_data=False)
    assert len(r)==3 and {"precision","runtime_seconds","throughput"}.issubset(r.columns)
