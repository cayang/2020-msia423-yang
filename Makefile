data/listings-clean.csv: data/neighbourhoods.csv
	python3 run.py clean

data/features.csv: data/listings-clean.csv
	python3 run.py features

models: data/features.csv
	python3 run.py train --use_existing_params=True

all: data/listings-clean.csv data/features.csv models

test_ingest_data:
	pytest test/test_ingest_data.py

test_clean_data:
	pytest test/test_clean_data.py

test_generate_features:
	pytest test/test_generate_features.py

test_train_model:
	pytest test/test_train_model.py

test_predict:
	pytest test/test_predict.py

tests_all: test_ingest_data test_clean_data test_generate_features test_train_model test_predict

.PHONY: all