from __future__ import annotations
from datetime import datetime, timezone
import numpy as np
import pandas as pd

ANOMALY_TYPES=["numeric_drift","margin_corruption","exchange_rate_drift","uom_corruption","currency_mismatch","phantom_delta","referential_integrity","temporal_corruption","collective_anomaly"]


def inject_anomalies(fact: pd.DataFrame, anomaly_rate: float, seed: int = 42, source_layer: str = "inbound") -> tuple[pd.DataFrame,pd.DataFrame]:
    rng=np.random.default_rng(seed)
    out=fact.copy().reset_index(drop=True)
    base_n=len(out)
    n=max(1,int(round(base_n*anomaly_rate))) if base_n else 0
    if n==0:
        return out, pd.DataFrame(columns=["anomaly_id","anomaly_type","affected_record","affected_fields","injection_timestamp","severity","ground_truth_label","source_layer","corruption_description","injection_method"])
    idx=rng.choice(base_n,size=min(n,base_n),replace=False)
    types=np.resize(np.array(ANOMALY_TYPES,dtype=object),len(idx))
    rng.shuffle(types)
    truth=[]
    now=datetime.now(timezone.utc).isoformat()
    phantom_rows=[]
    for seq,(i,atype) in enumerate(zip(idx,types),start=1):
        row=out.loc[i]
        rid=str(row["record_id"])
        severity="medium"; fields=[]; desc=""
        if atype=="numeric_drift":
            factor=float(rng.choice([0.08,0.12,6.0,10.0])); out.at[i,"quantity"]=max(.01,float(row["quantity"])*factor); fields=["quantity"]; desc=f"Quantity multiplied by {factor:.2f}."
        elif atype=="margin_corruption":
            out.at[i,"margin_doc"]=float(row["margin_doc"])+abs(float(row["revenue_doc"]))*float(rng.uniform(.35,.8)); fields=["margin_doc"]; severity="high"; desc="Stored margin made inconsistent with revenue minus cost."
        elif atype=="exchange_rate_drift":
            factor=float(rng.choice([.25,2.5,4.])); out.at[i,"exchange_rate"]=float(row["exchange_rate"])*factor; fields=["exchange_rate"]; severity="high"; desc="Exchange rate drift injected."
        elif atype=="uom_corruption":
            current=str(row.get("uom","EA")); choices=[u for u in ["EA","KG","L","BOX"] if u!=current]; out.at[i,"uom"]=rng.choice(choices); fields=["uom"]; desc="Transaction UoM changed to an incompatible value."
        elif atype=="currency_mismatch":
            current=str(row.get("document_currency","EUR")); choices=[c for c in ["EUR","USD","GBP","JPY"] if c!=current]; out.at[i,"document_currency"]=rng.choice(choices); fields=["document_currency"]; desc="Document currency changed without consistent semantic conversion."
        elif atype=="phantom_delta":
            dup=out.loc[i].copy(); dup["record_id"]=f"{rid}_PHANTOM"; phantom_rows.append(dup); fields=["sales_order_id","item_no"]; severity="high"; desc="Unexpected duplicate business key inserted as phantom delta."
        elif atype=="referential_integrity":
            out.at[i,"customer_id"]="C_MISSING"; fields=["customer_id"]; severity="high"; desc="Customer reference replaced with missing master-data key."
        elif atype=="temporal_corruption":
            order_date=pd.Timestamp(row["order_date"]); out.at[i,"delivery_date"]=order_date-pd.Timedelta(days=int(rng.integers(1,20))); fields=["delivery_date","order_date"]; severity="high"; desc="Delivery date moved before sales-order date."
        elif atype=="collective_anomaly":
            # A modest individual change becomes abnormal as a coordinated subgroup pattern.
            out.at[i,"unit_price"]=float(row["unit_price"])*1.55; out.at[i,"quantity"]=float(row["quantity"])*1.4; fields=["unit_price","quantity"]; desc="Coordinated moderate price and quantity shift injected."
        truth.append({"anomaly_id":f"A{seq:08d}","anomaly_type":atype,"affected_record":rid,"affected_fields":"|".join(fields),"injection_timestamp":now,"severity":severity,"ground_truth_label":1,"source_layer":source_layer,"corruption_description":desc,"injection_method":"controlled_synthetic_corruption"})
    if phantom_rows:
        out=pd.concat([out,pd.DataFrame(phantom_rows)],ignore_index=True)
    truth_df=pd.DataFrame(truth)
    return out,truth_df


def record_ground_truth(frame: pd.DataFrame, anomalies: pd.DataFrame) -> pd.DataFrame:
    anomaly_ids=set(anomalies["affected_record"].astype(str)) if len(anomalies) else set()
    gt=pd.DataFrame({"record_id":frame["record_id"].astype(str)})
    gt["ground_truth"]=gt.record_id.isin(anomaly_ids).astype(int)
    # phantom rows are also anomalous even though their source affected_record points to original key
    gt.loc[gt.record_id.str.endswith("_PHANTOM"),"ground_truth"]=1
    type_map=dict(zip(anomalies.affected_record.astype(str), anomalies.anomaly_type)) if len(anomalies) else {}
    gt["anomaly_type"]=gt.record_id.map(type_map)
    gt.loc[gt.record_id.str.endswith("_PHANTOM"),"anomaly_type"]="phantom_delta"
    return gt
