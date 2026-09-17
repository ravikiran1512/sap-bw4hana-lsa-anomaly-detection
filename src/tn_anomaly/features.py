from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULT_FEATURES=[
 "revenue_doc","cost_doc","margin_doc","quantity","unit_price","exchange_rate","revenue_local","cost_local",
 "margin_pct","order_to_delivery_days","delivery_to_billing_days","price_deviation_pct","cost_deviation_pct",
 "duplicate_frequency","customer_order_frequency","material_order_frequency","revenue_cost_ratio"
]

INBOUND_FEATURES=["revenue_doc","cost_doc","margin_doc","quantity","unit_price","exchange_rate","revenue_local","cost_local"]

def engineer_features(df: pd.DataFrame, layer: str = "harmonization") -> pd.DataFrame:
    x=df.copy()
    if "margin_pct" not in x and {"margin_doc","revenue_doc"}.issubset(x): x["margin_pct"]=x.margin_doc/x.revenue_doc.replace(0,np.nan)
    if "order_to_delivery_days" not in x and {"delivery_date","order_date"}.issubset(x): x["order_to_delivery_days"]=(pd.to_datetime(x.delivery_date)-pd.to_datetime(x.order_date)).dt.days
    if "delivery_to_billing_days" not in x and {"billing_date","delivery_date"}.issubset(x): x["delivery_to_billing_days"]=(pd.to_datetime(x.billing_date)-pd.to_datetime(x.delivery_date)).dt.days
    if "revenue_cost_ratio" not in x and {"revenue_doc","cost_doc"}.issubset(x): x["revenue_cost_ratio"]=x.revenue_doc/x.cost_doc.replace(0,np.nan)
    wanted=INBOUND_FEATURES if layer=="inbound" else DEFAULT_FEATURES
    cols=[c for c in wanted if c in x.columns]
    out=x[["record_id"]+cols].copy()
    for c in cols:
        out[c]=pd.to_numeric(out[c],errors="coerce")
        med=out[c].median()
        out[c]=out[c].fillna(0.0 if pd.isna(med) else med)
        out[c]=out[c].replace([np.inf,-np.inf],0.0)
    return out
