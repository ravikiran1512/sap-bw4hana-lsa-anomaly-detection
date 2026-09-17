from tn_anomaly.config import load_config
from tn_anomaly.data_generation import generate_enterprise_data
from tn_anomaly.harmonization import build_semantic_fact
from tn_anomaly.ml import detect_isolation_forest, detect_one_class_svm, detect_autoencoder

def _sample():
    cfg=load_config("config/small.yaml"); cfg["data"]["sales_orders"]=120; return build_semantic_fact(generate_enterprise_data(cfg,7)).head(300)

def test_ml_outputs():
    df=_sample()
    for func in [detect_isolation_forest, detect_one_class_svm]:
        pred,_=func(df,layer="harmonization"); assert len(pred)==len(df); assert set(pred.prediction.unique()).issubset({0,1})
    pred,_=detect_autoencoder(df,layer="harmonization",max_iter=30); assert len(pred)==len(df)
