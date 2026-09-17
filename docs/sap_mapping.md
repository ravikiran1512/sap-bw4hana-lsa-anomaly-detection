# SAP BW/4HANA LSA++ Mapping

| Project component | SAP BW/4HANA concept |
|---|---|
| Inbound raw layer | Inbound / Write-Interface ADSO |
| Harmonization layer | Standard ADSO |
| Transformation logic | BW Transformation |
| Load execution | DTP |
| Orchestration | Process Chain |
| Core data model | LSA++ propagation/core layer |
| Analytical semantic layer | CompositeProvider |
| Reporting | BW Query / analytical consumption |
| Data-quality checks | Transformation / validation logic |
| Anomaly engine | External/adjacent analytical service or controlled implementation |

The current executable implementation uses Python and files and is therefore an **architectural emulation**, not a deployed SAP BW/4HANA implementation.
