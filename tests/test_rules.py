from tn_anomaly.config import load_config
from tn_anomaly.data_generation import generate_enterprise_data
from tn_anomaly.harmonization import build_semantic_fact
from tn_anomaly.rules import detect_rules

def test_margin_rule_detects_inconsistency():
    cfg=load_config("config/small.yaml"); tables=generate_enterprise_data(cfg,42); fact=build_semantic_fact(tables).head(20).copy(); fact.loc[fact.index[0],"margin_doc"] += 9999
    pred=detect_rules(fact,tables)
    row=pred[pred.record_id==str(fact.iloc[0].record_id)].iloc[0]
    assert row.prediction==1 and "R002" in row.explanation
