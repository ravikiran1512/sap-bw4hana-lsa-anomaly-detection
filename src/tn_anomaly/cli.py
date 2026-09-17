from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from .config import load_config
from .pipeline import prepare_dataset, run_experiment, run_matrix
from .visualization import create_result_plots


def main():
    p=argparse.ArgumentParser(description="TechNova SAP BW/4HANA LSA++ anomaly-detection research emulator")
    p.add_argument("command",choices=["generate","experiment","plots","matrix"])
    p.add_argument("--config",default="config/small.yaml")
    args=p.parse_args(); cfg=load_config(args.config)
    if args.command=="generate":
        tables,corrupted,anomalies,gt=prepare_dataset(cfg,True); print(f"Generated {len(corrupted):,} semantic records with {len(gt[gt.ground_truth==1]):,} ground-truth anomalies.")
    elif args.command=="experiment":
        res=run_experiment(cfg,True); print(res[["layer","detector","precision","recall","f1","fdr","runtime_seconds","throughput"]].to_string(index=False))
    elif args.command=="plots":
        path=Path(cfg["experiment"]["output_dir"])/"experiment_results.csv"; df=pd.read_csv(path); paths=create_result_plots(df); print("\n".join(map(str,paths)))
    else:
        matrix=load_config("experiments/configs/matrix.yaml")
        res=run_matrix(cfg,matrix,persist_data=False)
        print(res[["dataset_size_label","seed","anomaly_rate","layer","detector","f1","runtime_seconds"]].to_string(index=False))

if __name__=="__main__": main()
