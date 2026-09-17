from tn_anomaly.config import load_config
from tn_anomaly.data_generation import generate_enterprise_data

def test_generation_reproducible():
    cfg=load_config("config/small.yaml"); a=generate_enterprise_data(cfg,42); b=generate_enterprise_data(cfg,42)
    assert a["sales_orders"].equals(b["sales_orders"])
    assert len(a["customers"])==cfg["data"]["customers"]
    assert {"sales_orders","sales_order_items","deliveries","billing_documents","finance_postings"}.issubset(a)
