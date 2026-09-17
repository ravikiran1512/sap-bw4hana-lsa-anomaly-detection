from __future__ import annotations
import numpy as np
import pandas as pd


def classification_metrics(y_true, y_pred) -> dict:
    y_true=np.asarray(y_true,dtype=int); y_pred=np.asarray(y_pred,dtype=int)
    tp=int(((y_true==1)&(y_pred==1)).sum()); fp=int(((y_true==0)&(y_pred==1)).sum()); tn=int(((y_true==0)&(y_pred==0)).sum()); fn=int(((y_true==1)&(y_pred==0)).sum())
    precision=tp/(tp+fp) if tp+fp else 0.; recall=tp/(tp+fn) if tp+fn else 0.; f1=2*precision*recall/(precision+recall) if precision+recall else 0.
    return {"tp":tp,"fp":fp,"tn":tn,"fn":fn,"precision":precision,"recall":recall,"f1":f1,"fdr":fp/(tp+fp) if tp+fp else 0.,"false_negative_rate":fn/(tp+fn) if tp+fn else 0.,"detection_rate":recall,"false_positive_rate":fp/(fp+tn) if fp+tn else 0.}

def evaluate_predictions(pred: pd.DataFrame, ground_truth: pd.DataFrame) -> tuple[dict,pd.DataFrame]:
    merged=ground_truth[["record_id","ground_truth"]].merge(pred,on="record_id",how="left")
    merged["prediction"]=merged.prediction.fillna(0).astype(int)
    return classification_metrics(merged.ground_truth,merged.prediction),merged

def threshold_sweep(scores, y_true, quantiles=(.90,.95,.975,.98,.99,.995)) -> pd.DataFrame:
    scores=np.asarray(scores,float); y=np.asarray(y_true,int); rows=[]
    for q in quantiles:
        th=float(np.quantile(scores,q)); m=classification_metrics(y,(scores>=th).astype(int)); rows.append({"quantile":q,"threshold":th,**m})
    return pd.DataFrame(rows)


def evaluate_by_anomaly_type(pred: pd.DataFrame, ground_truth: pd.DataFrame) -> pd.DataFrame:
    merged=ground_truth[["record_id","ground_truth","anomaly_type"]].merge(pred[["record_id","prediction"]],on="record_id",how="left")
    merged["prediction"]=merged.prediction.fillna(0).astype(int)
    rows=[]
    types=sorted(t for t in merged.anomaly_type.dropna().unique())
    for atype in types:
        y=(merged.anomaly_type==atype).astype(int)
        m=classification_metrics(y,merged.prediction)
        rows.append({"anomaly_type":atype,**m})
    return pd.DataFrame(rows)
