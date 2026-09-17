from __future__ import annotations
import numpy as np
import pandas as pd


def build_semantic_fact(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    items=tables["sales_order_items"].copy()
    orders=tables["sales_orders"].copy()
    materials=tables["materials"][["material_id","base_uom","material_group","standard_cost","list_price"]].copy()
    customers=tables["customers"][["customer_id","segment","preferred_currency"]].copy()
    deliveries=tables["deliveries"][["sales_order_id","delivery_id","delivery_date"]].copy()
    billing=tables["billing_documents"][["sales_order_id","billing_id","billing_date"]].copy()
    fact=(items.merge(orders,on="sales_order_id",how="left",suffixes=("","_hdr"))
              .merge(materials,on="material_id",how="left")
              .merge(customers,on="customer_id",how="left")
              .merge(deliveries,on="sales_order_id",how="left")
              .merge(billing,on="sales_order_id",how="left"))
    fact["margin_pct"]=np.where(fact.revenue_doc.abs()>1e-9,fact.margin_doc/fact.revenue_doc,np.nan)
    fact["order_to_delivery_days"]=(pd.to_datetime(fact.delivery_date)-pd.to_datetime(fact.order_date)).dt.days
    fact["delivery_to_billing_days"]=(pd.to_datetime(fact.billing_date)-pd.to_datetime(fact.delivery_date)).dt.days
    fact["expected_margin_doc"]=fact.revenue_doc-fact.cost_doc
    fact["price_deviation_pct"]=(fact.unit_price-fact.list_price)/fact.list_price.replace(0,np.nan)
    fact["cost_deviation_pct"]=(fact.cost_doc/fact.quantity-fact.standard_cost)/fact.standard_cost.replace(0,np.nan)
    fact["duplicate_frequency"]=fact.groupby(["sales_order_id","item_no"])["record_id"].transform("size")
    fact["customer_order_frequency"]=fact.groupby("customer_id")["sales_order_id"].transform("nunique")
    fact["material_order_frequency"]=fact.groupby("material_id")["sales_order_id"].transform("nunique")
    fact["revenue_cost_ratio"]=fact.revenue_doc/fact.cost_doc.replace(0,np.nan)
    return fact


def layer_view(fact: pd.DataFrame, layer: str) -> pd.DataFrame:
    if layer == "inbound":
        # Represents fields normally available near acquisition/staging before full semantic enrichment.
        keep=["record_id","sales_order_id","item_no","customer_id","material_id","plant_id","order_date",
              "document_currency","uom","quantity","unit_price","revenue_doc","cost_doc","margin_doc","exchange_rate",
              "revenue_local","cost_local","delivery_date","billing_date","base_uom","preferred_currency"]
        return fact[[c for c in keep if c in fact.columns]].copy()
    if layer in {"harmonization","analytical"}:
        return fact.copy()
    raise ValueError(f"Unknown layer: {layer}")
