from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import RobustScaler
from .features import engineer_features


def _split_scale(df: pd.DataFrame, layer: str):
    f=engineer_features(df,layer)
    X=f.drop(columns="record_id").to_numpy(dtype=float)
    n_train=max(10,int(len(X)*.6))
    scaler=RobustScaler().fit(X[:n_train])
    return f,scaler.transform(X),n_train,scaler

def _threshold(scores: np.ndarray, train_n: int, quantile: float):
    return float(np.quantile(scores[:train_n], quantile))

def detect_isolation_forest(df: pd.DataFrame, layer: str="harmonization", seed: int=42, threshold_quantile: float=.98, n_estimators: int=150):
    f,X,n_train,_=_split_scale(df,layer)
    model=IsolationForest(n_estimators=n_estimators,contamination="auto",random_state=seed,n_jobs=-1).fit(X[:n_train])
    scores=-model.score_samples(X); th=_threshold(scores,n_train,threshold_quantile); pred=(scores>=th).astype(int)
    return pd.DataFrame({"record_id":f.record_id.astype(str),"anomaly_score":scores,"threshold":th,"prediction":pred,"explanation":[f"Isolation score {s:.4f} vs threshold {th:.4f}" for s in scores]}),model

def detect_one_class_svm(df: pd.DataFrame, layer: str="harmonization", nu: float=.02, gamma="scale", threshold_quantile: float=.98):
    f,X,n_train,_=_split_scale(df,layer)
    # OCSVM is O(n^2+) in practice; bounded training sample keeps matrix experiments reproducible.
    train=X[:min(n_train,10000)]
    model=OneClassSVM(nu=nu,gamma=gamma,kernel="rbf").fit(train)
    scores=-model.decision_function(X).ravel(); th=_threshold(scores,min(n_train,len(scores)),threshold_quantile); pred=(scores>=th).astype(int)
    return pd.DataFrame({"record_id":f.record_id.astype(str),"anomaly_score":scores,"threshold":th,"prediction":pred,"explanation":[f"OCSVM score {s:.4f} vs threshold {th:.4f}" for s in scores]}),model

def detect_autoencoder(df: pd.DataFrame, layer: str="harmonization", seed: int=42, hidden_layer_sizes=(16,6,16), max_iter=250, alpha=.0001, threshold_quantile=.98):
    f,X,n_train,_=_split_scale(df,layer)
    # Lightweight fully-connected reconstruction autoencoder using sklearn MLPRegressor.
    model=MLPRegressor(hidden_layer_sizes=tuple(hidden_layer_sizes),activation="relu",solver="adam",alpha=alpha,max_iter=max_iter,random_state=seed,early_stopping=True,validation_fraction=.15).fit(X[:n_train],X[:n_train])
    recon=model.predict(X); scores=((X-recon)**2).mean(axis=1); th=_threshold(scores,n_train,threshold_quantile); pred=(scores>=th).astype(int)
    return pd.DataFrame({"record_id":f.record_id.astype(str),"anomaly_score":scores,"threshold":th,"prediction":pred,"explanation":[f"Reconstruction MSE {s:.6f} vs threshold {th:.6f}" for s in scores]}),model
