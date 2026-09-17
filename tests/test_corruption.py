from tn_anomaly.config import load_config
from tn_anomaly.data_generation import generate_enterprise_data
from tn_anomaly.harmonization import build_semantic_fact
from tn_anomaly.corruption import inject_anomalies, record_ground_truth

def test_corruption_and_ground_truth():
    cfg=load_config("config/small.yaml"); fact=build_semantic_fact(generate_enterprise_data(cfg,42)); bad,log=inject_anomalies(fact,.02,142); gt=record_ground_truth(bad,log)
    assert len(log)>0
    assert gt.ground_truth.sum()>=len(log)
    assert log.anomaly_type.nunique()>=5
