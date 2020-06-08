data/listings-clean.csv: data/neighbourhoods.csv
	python3 run.py clean

data/features.csv: data/listings-clean.csv
	python3 run.py features

models: data/features.csv
	python3 run.py train --use_existing_params=True

all: data/listings-clean.csv data/features.csv models

.PHONY: all