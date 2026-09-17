# Experiment Protocol

1. Select a configuration, random seed, dataset size and anomaly rate.
2. Generate clean synthetic O2C/Finance data.
3. Create the harmonized semantic fact.
4. Inject controlled corruptions and persist ground truth.
5. Build the requested architectural layer view.
6. Execute baseline/detector variants under the benchmark wrapper.
7. Persist predictions, metrics and performance measures.
8. Repeat across seeds and calculate mean, standard deviation and confidence intervals before answering research questions.

Default detectors: rules, Z-score, IQR, Isolation Forest, One-Class SVM, autoencoder. Default layers: inbound and harmonization. The full matrix configuration includes small/medium/large conceptual sizes and 0.5%, 1%, 2%, 3%, 5% anomaly rates.

Do not use one smoke-test run to claim that RQ1–RQ3 are answered.
