# SAP BW/4HANA Architecture Mapping

The executable repository is an **SAP BW/4HANA architectural emulation** unless connected to a real BW/4HANA system. Python, CSV and optional PostgreSQL components are not represented as SAP objects.

Proposed real-system object names:

| Purpose | Proposed BW/4HANA object |
|---|---|
| Inbound sales | `ZTN_IN_SALES` |
| Harmonized sales | `ZTN_HARM_SALES` |
| Core sales | `ZTN_CORE_SALES` |
| CompositeProvider | `ZTN_CPROV_SALES` |
| BW Query | `ZTN_Q_SALES` |

External ML integration is designed as an adjacent analytical service. A productive implementation must define security, data minimization, authentication, operational ownership, retry/idempotency, and monitoring before moving warehouse records across system boundaries.
