from __future__ import annotations
import numpy as np
import pandas as pd

CURRENCIES = ["EUR", "USD", "GBP", "JPY", "CHF"]
UOMS = ["EA", "KG", "L", "BOX"]


def _ids(prefix: str, n: int, width: int = 6):
    return [f"{prefix}{i:0{width}d}" for i in range(1, n + 1)]


def generate_enterprise_data(cfg: dict, seed: int | None = None) -> dict[str, pd.DataFrame]:
    dcfg = cfg["data"]
    seed = cfg["project"]["random_seed"] if seed is None else seed
    rng = np.random.default_rng(seed)
    start, end = pd.Timestamp(dcfg["start_date"]), pd.Timestamp(dcfg["end_date"])
    days = pd.date_range(start, end, freq="D")

    customer_ids = _ids("C", int(dcfg["customers"]))
    material_ids = _ids("M", int(dcfg["materials"]))
    plant_ids = _ids("P", int(dcfg.get("plants", 5)), 3)
    warehouse_ids = _ids("W", int(dcfg.get("warehouses", 8)), 3)
    sales_org_ids = _ids("SO", int(dcfg.get("sales_organizations", 4)), 3)

    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_sk": np.arange(1, len(customer_ids)+1),
        "country": rng.choice(["DE", "FR", "NL", "US", "GB", "CH"], len(customer_ids), p=[.35,.15,.1,.15,.15,.1]),
        "segment": rng.choice(["SMB", "MID", "ENTERPRISE"], len(customer_ids), p=[.45,.35,.2]),
        "preferred_currency": rng.choice(CURRENCIES[:3], len(customer_ids), p=[.65,.22,.13]),
        "valid_from": start,
        "valid_to": pd.NaT,
        "is_current": True,
    })

    base_cost = rng.lognormal(mean=4.1, sigma=.65, size=len(material_ids)).round(2)
    materials = pd.DataFrame({
        "material_id": material_ids,
        "material_sk": np.arange(1, len(material_ids)+1),
        "material_group": rng.choice(["ELECTRONICS", "MECHANICAL", "PACKAGING", "CHEMICAL"], len(material_ids)),
        "base_uom": rng.choice(UOMS, len(material_ids), p=[.55,.18,.12,.15]),
        "standard_cost": base_cost,
        "list_price": (base_cost * rng.uniform(1.18, 1.9, len(material_ids))).round(2),
        "valid_from": start,
        "valid_to": pd.NaT,
        "is_current": True,
    })

    plants = pd.DataFrame({"plant_id": plant_ids, "country": rng.choice(["DE","NL","FR"], len(plant_ids)), "currency":"EUR"})
    warehouses = pd.DataFrame({"warehouse_id": warehouse_ids, "plant_id": rng.choice(plant_ids, len(warehouse_ids))})
    sales_orgs = pd.DataFrame({"sales_org_id": sales_org_ids, "currency": rng.choice(["EUR","USD","GBP"], len(sales_org_ids), p=[.6,.25,.15])})
    currencies = pd.DataFrame({"currency": CURRENCIES, "decimals": [2,2,2,0,2]})
    uom = pd.DataFrame({"uom": UOMS, "dimension": ["COUNT","MASS","VOLUME","COUNT"]})

    # Synthetic historical FX: local EUR per 1 unit document currency.
    anchors = {"EUR":1.0,"USD":.92,"GBP":1.17,"JPY":.0062,"CHF":1.04}
    fx_rows=[]
    for cur in CURRENCIES:
        level=anchors[cur]
        walk=rng.normal(0, max(abs(level)*0.002, 1e-5), len(days)).cumsum()
        vals=np.clip(level+walk, level*.75, level*1.25)
        for dt,val in zip(days,vals):
            fx_rows.append((cur,"EUR",dt,float(val)))
    exchange_rates=pd.DataFrame(fx_rows, columns=["from_currency","to_currency","rate_date","exchange_rate"])

    n_orders=int(dcfg["sales_orders"])
    order_ids=_ids("ORD", n_orders, 8)
    order_dates=rng.choice(days, n_orders)
    cust_for_order=rng.choice(customer_ids, n_orders)
    org_for_order=rng.choice(sales_org_ids, n_orders)
    org_currency=dict(zip(sales_orgs.sales_org_id, sales_orgs.currency))
    orders=pd.DataFrame({
        "sales_order_id": order_ids,
        "customer_id": cust_for_order,
        "sales_org_id": org_for_order,
        "plant_id": rng.choice(plant_ids, n_orders),
        "order_date": pd.to_datetime(order_dates),
        "document_currency": [org_currency[o] for o in org_for_order],
        "load_batch_id": rng.integers(1, 13, n_orders),
    })

    avg=max(1, int(dcfg.get("avg_items_per_order", 3)))
    item_counts=np.clip(rng.poisson(avg-1, n_orders)+1,1,8)
    item_rows=[]
    item_id=0
    mat_index=materials.set_index("material_id")
    fx_index=exchange_rates.set_index(["from_currency","rate_date"])["exchange_rate"]
    for order, count in zip(orders.itertuples(index=False), item_counts):
        for item_no in range(10, 10*(count+1), 10):
            item_id += 1
            mid=rng.choice(material_ids)
            m=mat_index.loc[mid]
            qty=float(max(1, rng.lognormal(mean=1.45, sigma=.65)))
            price=float(m.list_price*rng.normal(1.0,.06))
            cost=float(m.standard_cost*qty*rng.normal(1.0,.025))
            revenue=float(price*qty)
            rate=float(fx_index.loc[(order.document_currency, pd.Timestamp(order.order_date))])
            item_rows.append((f"ITEM{item_id:010d}",order.sales_order_id,item_no,mid,m.base_uom,qty,price,revenue,cost,revenue-cost,order.document_currency,rate,revenue*rate,cost*rate))
    order_items=pd.DataFrame(item_rows, columns=["record_id","sales_order_id","item_no","material_id","uom","quantity","unit_price","revenue_doc","cost_doc","margin_doc","document_currency","exchange_rate","revenue_local","cost_local"])

    # deliveries and billing are 1:1 to order at document header level when present
    delivered_mask=rng.random(n_orders) < float(dcfg.get("delivery_rate",.92))
    delivered_orders=orders.loc[delivered_mask].copy()
    lead=rng.integers(1,15,len(delivered_orders))
    deliveries=pd.DataFrame({
        "delivery_id": _ids("DEL",len(delivered_orders),8),
        "sales_order_id": delivered_orders.sales_order_id.to_numpy(),
        "delivery_date": delivered_orders.order_date.to_numpy()+pd.to_timedelta(lead,unit="D"),
        "warehouse_id": rng.choice(warehouse_ids,len(delivered_orders)),
    })
    delivered_item_map=order_items.merge(deliveries[["delivery_id","sales_order_id"]],on="sales_order_id",how="inner")
    delivery_items=delivered_item_map[["delivery_id","record_id","material_id","quantity","uom"]].copy()
    delivery_items=delivery_items.rename(columns={"record_id":"sales_order_item_id","quantity":"delivered_quantity"})
    delivery_items.insert(0,"delivery_item_id",_ids("DELI",len(delivery_items),10))

    billed_mask=rng.random(len(deliveries)) < float(dcfg.get("billing_rate",.95))
    billed_deliveries=deliveries.loc[billed_mask].copy()
    bill_lag=rng.integers(0,7,len(billed_deliveries))
    billing=pd.DataFrame({
        "billing_id":_ids("BIL",len(billed_deliveries),8),
        "delivery_id":billed_deliveries.delivery_id.to_numpy(),
        "sales_order_id":billed_deliveries.sales_order_id.to_numpy(),
        "billing_date":billed_deliveries.delivery_date.to_numpy()+pd.to_timedelta(bill_lag,unit="D"),
    })
    bill_items=order_items.merge(billing[["billing_id","sales_order_id"]],on="sales_order_id",how="inner")
    billing_items=bill_items[["billing_id","record_id","revenue_doc","document_currency"]].copy().rename(columns={"record_id":"sales_order_item_id","revenue_doc":"billed_amount"})
    billing_items.insert(0,"billing_item_id",_ids("BILI",len(billing_items),10))

    fin_mask=rng.random(len(billing)) < float(dcfg.get("finance_rate",.98))
    fin_bill=billing.loc[fin_mask].copy()
    post_lag=rng.integers(0,4,len(fin_bill))
    finance=pd.DataFrame({
        "finance_posting_id":_ids("FIN",len(fin_bill),9),
        "billing_id":fin_bill.billing_id.to_numpy(),
        "posting_date":fin_bill.billing_date.to_numpy()+pd.to_timedelta(post_lag,unit="D"),
        "company_code":"TN01",
        "local_currency":"EUR",
    })
    bill_sum=billing_items.groupby("billing_id",as_index=False).billed_amount.sum()
    finance=finance.merge(bill_sum,on="billing_id",how="left").rename(columns={"billed_amount":"document_amount"})

    return {
        "customers":customers,"materials":materials,"plants":plants,"warehouses":warehouses,
        "sales_organizations":sales_orgs,"currencies":currencies,"units_of_measure":uom,
        "exchange_rates":exchange_rates,"sales_orders":orders,"sales_order_items":order_items,
        "deliveries":deliveries,"delivery_items":delivery_items,"billing_documents":billing,
        "billing_items":billing_items,"finance_postings":finance,
    }
