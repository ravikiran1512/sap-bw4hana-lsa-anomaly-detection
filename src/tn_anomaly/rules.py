from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    description: str

RULES=[
 Rule("R001","negative_margin","Margin cannot be negative unless permitted."),
 Rule("R002","margin_equation","Stored margin must equal revenue minus cost."),
 Rule("R003","currency_master","Document currency must exist in currency master."),
 Rule("R005","uom_compatibility","Transaction UoM must match material base UoM in this simplified emulation."),
 Rule("R006","customer_master","Customer must exist in customer master."),
 Rule("R007","material_master","Material must exist in material master."),
 Rule("R008","delivery_sequence","Delivery cannot precede order."),
 Rule("R009","billing_sequence","Billing cannot precede delivery."),
 Rule("R010","duplicate_business_key","Sales-order/item business key must be unique."),
 Rule("R011","exchange_rate_positive","Exchange rate must be positive and within a broad plausibility band."),
]

def detect_rules(df: pd.DataFrame, masters: dict | None = None) -> pd.DataFrame:
    n=len(df); hits=[]
    duplicate=df.duplicated([c for c in ["sales_order_id","item_no"] if c in df.columns],keep=False) if {"sales_order_id","item_no"}.issubset(df.columns) else pd.Series(False,index=df.index)
    valid_customers=set(masters["customers"].customer_id) if masters and "customers" in masters else set(df.get("customer_id",[]))
    valid_materials=set(masters["materials"].material_id) if masters and "materials" in masters else set(df.get("material_id",[]))
    valid_currencies=set(masters["currencies"].currency) if masters and "currencies" in masters else {"EUR","USD","GBP","JPY","CHF"}
    for i,row in df.iterrows():
        reasons=[]
        rev=float(row.get("revenue_doc",np.nan)); cost=float(row.get("cost_doc",np.nan)); margin=float(row.get("margin_doc",np.nan))
        if np.isfinite(margin) and margin < 0: reasons.append("R001: negative margin")
        if np.isfinite(rev) and np.isfinite(cost) and np.isfinite(margin) and not np.isclose(margin,rev-cost,rtol=1e-6,atol=.01): reasons.append(f"R002: expected margin {rev-cost:.2f}, observed {margin:.2f}")
        if str(row.get("document_currency")) not in valid_currencies: reasons.append("R003: unknown currency")
        if "base_uom" in row and pd.notna(row.get("base_uom")) and str(row.get("uom")) != str(row.get("base_uom")): reasons.append(f"R005: expected UoM {row.get('base_uom')}, observed {row.get('uom')}")
        if str(row.get("customer_id")) not in valid_customers: reasons.append("R006: missing customer")
        if str(row.get("material_id")) not in valid_materials: reasons.append("R007: missing material")
        if pd.notna(row.get("delivery_date")) and pd.Timestamp(row["delivery_date"]) < pd.Timestamp(row["order_date"]): reasons.append("R008: delivery before order")
        if pd.notna(row.get("billing_date")) and pd.notna(row.get("delivery_date")) and pd.Timestamp(row["billing_date"]) < pd.Timestamp(row["delivery_date"]): reasons.append("R009: billing before delivery")
        if bool(duplicate.loc[i]): reasons.append("R010: duplicate business key")
        rate=float(row.get("exchange_rate",1.0))
        if (not np.isfinite(rate)) or rate <= 0 or rate > 10: reasons.append(f"R011: implausible exchange rate {rate}")
        score=min(1.0, len(reasons)/3.0)
        hits.append({"record_id":str(row["record_id"]),"anomaly_score":score,"prediction":int(bool(reasons)),"explanation":"; ".join(reasons) or "No configured rule violation."})
    return pd.DataFrame(hits)
