from tn_anomaly.evaluation import classification_metrics
from tn_anomaly.features import engineer_features
import pandas as pd

def test_metrics():
    m=classification_metrics([1,1,0,0],[1,0,1,0]); assert m["precision"]==.5 and m["recall"]==.5 and m["fdr"]==.5

def test_feature_engineering_minimal():
    df=pd.DataFrame({"record_id":["1"],"revenue_doc":[10.],"cost_doc":[8.],"margin_doc":[2.],"quantity":[1.],"unit_price":[10.],"exchange_rate":[1.],"revenue_local":[10.],"cost_local":[8.]})
    f=engineer_features(df,"inbound"); assert "record_id" in f and len(f)==1
