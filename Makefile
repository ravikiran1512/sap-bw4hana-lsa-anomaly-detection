PYTHON ?= python
CONFIG ?= config/small.yaml

.PHONY: install test generate experiment plots
install:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

test:
	pytest

generate:
	$(PYTHON) -m tn_anomaly.cli generate --config $(CONFIG)

experiment:
	$(PYTHON) -m tn_anomaly.cli experiment --config $(CONFIG)

plots:
	$(PYTHON) -m tn_anomaly.cli plots --config $(CONFIG)
