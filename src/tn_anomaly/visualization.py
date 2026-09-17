from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

METRICS=["precision","recall","f1","fdr","runtime_seconds","memory_mb","throughput","mttd"]

def create_result_plots(results: pd.DataFrame, out_dir: str|Path="experiments/results/figures"):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True); paths=[]
    if results.empty: return paths
    for metric in METRICS:
        if metric not in results: continue
        pivot=results.pivot_table(index="detector",columns="layer",values=metric,aggfunc="mean")
        ax=pivot.plot(kind="bar",figsize=(10,5))
        ax.set_title(f"{metric.replace('_',' ').title()} by Detector and LSA++-Style Layer")
        ax.set_ylabel(metric.replace('_',' ').title()); ax.set_xlabel("Detector"); ax.grid(axis="y",alpha=.25)
        plt.tight_layout(); p=out/f"{metric}.png"; plt.savefig(p,dpi=180); plt.close(); paths.append(p)
    return paths
