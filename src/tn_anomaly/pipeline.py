from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
from .data_generation import generate_enterprise_data
from .harmonization import build_semantic_fact, layer_view
from .corruption import inject_anomalies, record_ground_truth
from .rules import detect_rules
from .statistical import detect_zscore, detect_iqr
from .ml import detect_isolation_forest, detect_one_class_svm, detect_autoencoder
from .evaluation import evaluate_predictions, evaluate_by_anomaly_type
from .benchmarking import measure
from .results import append_result


def _detector(name, df, layer, cfg, masters, seed):
    q=float(cfg["models"].get("threshold_quantile",.98))
    if name=="baseline": return pd.DataFrame({"record_id":df["record_id"].astype(str),"anomaly_score":0.0,"threshold":None,"prediction":0,"explanation":"No anomaly detection baseline."})
    if name=="rules": return detect_rules(df,masters)
    if name=="zscore": return detect_zscore(df,layer)
    if name=="iqr": return detect_iqr(df,layer)
    if name=="isolation_forest": return detect_isolation_forest(df,layer,seed,q,int(cfg["models"]["isolation_forest"].get("n_estimators",150)))[0]
    if name=="one_class_svm":
        c=cfg["models"]["one_class_svm"]; return detect_one_class_svm(df,layer,float(c.get("nu",.02)),c.get("gamma","scale"),q)[0]
    if name=="autoencoder":
        c=cfg["models"]["autoencoder"]; return detect_autoencoder(df,layer,seed,tuple(c.get("hidden_layer_sizes",[16,6,16])),int(c.get("max_iter",250)),float(c.get("alpha",.0001)),q)[0]
    raise ValueError(name)


def prepare_dataset(cfg: dict, persist: bool=True):
    seed=int(cfg["project"]["random_seed"]); tables=generate_enterprise_data(cfg,seed); fact=build_semantic_fact(tables)
    corrupted, anomalies=inject_anomalies(fact,float(cfg["corruption"]["anomaly_rate"]),seed+100,str(cfg["corruption"].get("source_layer","inbound")))
    gt=record_ground_truth(corrupted,anomalies)
    if persist:
        for d in ["data/raw","data/processed","data/ground_truth"]: Path(d).mkdir(parents=True,exist_ok=True)
        for name,df in tables.items(): df.to_csv(Path("data/raw")/f"{name}.csv",index=False)
        fact.to_csv("data/processed/semantic_fact_clean.csv",index=False); corrupted.to_csv("data/processed/semantic_fact_corrupted.csv",index=False); anomalies.to_csv("data/ground_truth/anomaly_ground_truth.csv",index=False); gt.to_csv("data/ground_truth/record_ground_truth.csv",index=False)
    return tables,corrupted,anomalies,gt


def run_experiment(cfg: dict, persist_data: bool=True, detectors: list[str]|None=None, layers: list[str]|None=None):
    tables,corrupted,anomalies,gt=prepare_dataset(cfg,persist_data)
    detectors=detectors or list(cfg["experiment"]["detectors"]); layers=layers or list(cfg["experiment"]["layers"])
    rows=[]; result_path=Path(cfg["experiment"]["output_dir"])/"experiment_results.csv"; seed=int(cfg["project"]["random_seed"])
    for layer in layers:
        view=layer_view(corrupted,layer)
        for name in detectors:
            with measure(len(view)) as box:
                pred=_detector(name,view,layer,cfg,tables,seed)
            metrics, merged=evaluate_predictions(pred,gt)
            bm=box["benchmark"]
            # Batch emulation: injection timestamp is recorded, but wall-clock MTTD would be dominated by orchestration; use processing latency as reproducible proxy and label docs accordingly.
            mttd=bm.runtime_seconds
            row={"dataset_size":len(view),"anomaly_rate":float(cfg["corruption"]["anomaly_rate"]),"layer":layer,"detector":name,"model_version":"0.1.0",**{k:metrics[k] for k in ["precision","recall","f1","fdr"]},"mttd":mttd,"runtime_seconds":bm.runtime_seconds,"memory_mb":bm.memory_mb,"cpu_usage":bm.cpu_usage,"records_processed":bm.records_processed,"throughput":bm.throughput}
            full=append_result(row,result_path); rows.append(full)
            outdir=Path(cfg["experiment"]["run_dir"])/full["experiment_id"]; outdir.mkdir(parents=True,exist_ok=True)
            pred.to_csv(outdir/f"{layer}_{name}_predictions.csv",index=False)
            per_type=evaluate_by_anomaly_type(pred,gt)
            per_type.to_csv(outdir/f"{layer}_{name}_per_corruption_metrics.csv",index=False)
            detector_type=("baseline" if name=="baseline" else "rule" if name=="rules" else "statistical" if name in {"zscore","iqr"} else "ml")
            std=gt.merge(pred,on="record_id",how="left")
            now=datetime.now(timezone.utc).isoformat()
            std["anomaly_result_id"]=[f"{full['experiment_id']}-{i:08d}" for i in range(len(std))]
            std["layer"]=layer; std["detector_type"]=detector_type; std["detector_name"]=name
            std["detection_timestamp"]=now; std["processing_timestamp"]=now; std["severity"]=None
            if "threshold" not in std: std["threshold"]=None
            cols=["anomaly_result_id","record_id","layer","detector_type","detector_name","anomaly_type","anomaly_score","threshold","prediction","ground_truth","detection_timestamp","processing_timestamp","severity","explanation"]
            std[cols].to_csv(outdir/f"{layer}_{name}_anomaly_results.csv",index=False)
            with open(outdir/"metrics.json","w",encoding="utf-8") as fh: json.dump(row,fh,indent=2,default=str)
    return pd.DataFrame(rows)


def run_matrix(base_cfg: dict, matrix_cfg: dict, persist_data: bool=False) -> pd.DataFrame:
    """Execute the configured dataset-size × anomaly-rate × detector × layer × seed matrix.

    `dataset_sizes` map to requested sales-order counts in this emulation. Each run is
    reproducible and appends measured results; callers should choose a practical subset
    for local hardware when the full matrix is large.
    """
    import copy
    all_rows=[]
    for size_name,order_count in matrix_cfg["dataset_sizes"].items():
        for rate in matrix_cfg["anomaly_rates"]:
            for seed in matrix_cfg.get("seeds",[base_cfg["project"]["random_seed"]]):
                cfg=copy.deepcopy(base_cfg)
                cfg["data"]["sales_orders"]=int(order_count)
                cfg["corruption"]["anomaly_rate"]=float(rate)
                cfg["project"]["random_seed"]=int(seed)
                r=run_experiment(cfg,persist_data=persist_data,detectors=list(matrix_cfg["detectors"]),layers=list(matrix_cfg["layers"]))
                r["dataset_size_label"]=size_name; r["seed"]=seed; all_rows.append(r)
    return pd.concat(all_rows,ignore_index=True) if all_rows else pd.DataFrame()
