from __future__ import annotations
import numpy as np
import pandas as pd
from .features import engineer_features


def detect_zscore(df: pd.DataFrame, layer: str="harmonization", threshold: float=3.5) -> pd.DataFrame:
    f=engineer_features(df,layer)
    X=f.drop(columns="record_id")
    mean=X.mean(); std=X.std(ddof=0).replace(0,1)
    z=((X-mean)/std).abs()
    score=z.max(axis=1)
    pred=(score>threshold).astype(int)
    top=z.idxmax(axis=1) if len(X.columns) else pd.Series("none",index=X.index)
    expl=[f"max |z|={s:.3f} on {t}" for s,t in zip(score,top)]
    return pd.DataFrame({"record_id":f.record_id.astype(str),"anomaly_score":score,"prediction":pred,"explanation":expl})


def detect_iqr(df: pd.DataFrame, layer: str="harmonization", multiplier: float=2.5) -> pd.DataFrame:
    f=engineer_features(df,layer); X=f.drop(columns="record_id")
    q1=X.quantile(.25); q3=X.quantile(.75); iqr=(q3-q1).replace(0,1)
    low=q1-multiplier*iqr; high=q3+multiplier*iqr
    norm_dev=pd.DataFrame(index=X.index)
    for c in X.columns:
        norm_dev[c]=np.maximum((low[c]-X[c])/iqr[c],(X[c]-high[c])/iqr[c]).clip(lower=0)
    score=norm_dev.max(axis=1); pred=(score>0).astype(int)
    top=norm_dev.idxmax(axis=1) if len(X.columns) else pd.Series("none",index=X.index)
    return pd.DataFrame({"record_id":f.record_id.astype(str),"anomaly_score":score,"prediction":pred,"explanation":[f"IQR deviation={s:.3f} on {t}" for s,t in zip(score,top)]})


def rolling_zscore(series: pd.Series, window: int=30, threshold: float=3.0) -> pd.Series:
    mean=series.rolling(window,min_periods=max(5,window//4)).mean()
    std=series.rolling(window,min_periods=max(5,window//4)).std().replace(0,np.nan)
    return ((series-mean)/std).abs().gt(threshold).fillna(False).astype(int)


def rolling_iqr(series: pd.Series, window: int=30, multiplier: float=2.5) -> pd.Series:
    q1=series.rolling(window,min_periods=max(5,window//4)).quantile(.25)
    q3=series.rolling(window,min_periods=max(5,window//4)).quantile(.75)
    iqr=(q3-q1).replace(0,np.nan)
    low=q1-multiplier*iqr; high=q3+multiplier*iqr
    return ((series<low)|(series>high)).fillna(False).astype(int)


def moving_average_deviation(series: pd.Series, window: int=30, std_multiplier: float=3.0) -> pd.DataFrame:
    mean=series.rolling(window,min_periods=max(5,window//4)).mean()
    std=series.rolling(window,min_periods=max(5,window//4)).std().replace(0,np.nan)
    score=((series-mean)/std).abs()
    return pd.DataFrame({"moving_average":mean,"moving_std":std,"deviation_score":score,"prediction":score.gt(std_multiplier).fillna(False).astype(int)})


def percentile_detection(series: pd.Series, lower_q: float=.005, upper_q: float=.995) -> pd.DataFrame:
    low=float(series.quantile(lower_q)); high=float(series.quantile(upper_q))
    pred=((series<low)|(series>high)).astype(int)
    distance=np.maximum((low-series).clip(lower=0),(series-high).clip(lower=0))
    return pd.DataFrame({"lower_threshold":low,"upper_threshold":high,"anomaly_score":distance,"prediction":pred})


def dynamic_threshold(scores: pd.Series, window: int=50, quantile: float=.98) -> pd.Series:
    return scores.rolling(window,min_periods=max(10,window//4)).quantile(quantile)
