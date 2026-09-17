# Data Model

All entities are synthetic and SAP-inspired; none are represented as actual SAP tables.

| Entity | Grain / key | Notes |
|---|---|---|
| Customer | one row per `customer_id` / surrogate `customer_sk` | SCD-compatible validity columns |
| Material | one row per `material_id` / surrogate `material_sk` | base UoM, cost and list price |
| Plant | one row per plant | organizational master |
| Warehouse | one row per warehouse | many warehouses to a plant |
| Sales Organization | one row per sales org | expected document currency |
| Currency | one row per ISO-like currency | reference master |
| Unit of Measure | one row per UoM | semantic dimension |
| Exchange Rate | currency/date | historical rate to EUR |
| Sales Order | one row per order | header business key |
| Sales Order Item | one row per order/item | primary transaction grain used by detector |
| Delivery / Item | document / document-item | references order |
| Billing / Item | document / document-item | references delivery/order |
| Finance Posting | one row per posting | references billing |

The harmonized semantic fact keeps `record_id` as the detector key and derives ratios, lead times, duplicate frequency, customer/material frequency, and deviation features.
