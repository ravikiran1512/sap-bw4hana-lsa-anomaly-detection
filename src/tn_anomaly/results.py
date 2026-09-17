from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import uuid
import pandas as pd

RESULT_COLUMNS=["experiment_id","run_timestamp","dataset_size","anomaly_rate","layer","detector","model_version","precision","recall","f1","fdr","mttd","runtime_seconds","memory_mb","cpu_usage","records_processed","throughput"]

def append_result(row: dict, path: str | Path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    full={"experiment_id":row.get("experiment_id",str(uuid.uuid4())),"run_timestamp":row.get("run_timestamp",datetime.now(timezone.utc).isoformat()),**row}
    df=pd.DataFrame([{c:full.get(c) for c in RESULT_COLUMNS}])
    if path.exists(): df.to_csv(path,mode="a",header=False,index=False)
    else: df.to_csv(path,index=False)
    return full
