REGION		:= us-west-2
SLS_DEBUG	:= *

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]].*:' Makefile

install-sls:
	npm install

deploy-prod:
	SLS_DEBUG=$(SLS_DEBUG) STAGE=prod ./node_modules/.bin/sls deploy --region $(REGION) --stage prod

remove-deploy-prod:
	echo "Warning: removing deployement"
	SLS_DEBUG=$(SLS_DEBUG) STAGE=prod ./node_modules/.bin/sls remove --region $(REGION) --stage prod

deploy-dev:
	SLS_DEBUG=$(SLS_DEBUG) STAGE=dev ./node_modules/.bin/sls deploy --region $(REGION) --stage dev

remove-deploy-dev:
	echo "Warning: removing deployement"
	SLS_DEBUG=$(SLS_DEBUG) STAGE=dev ./node_modules/.bin/sls remove --region $(REGION) --stage dev

python-venv:
	$(shell [ -d venv ] || python3 -m venv venv)
	echo "# Run this in your shell to activate:"
	echo "source venv/bin/activate"

tests:
	flake8 *.py
	flake8 tests
	python -m unittest discover tests

clean:
	rm -rf node_modules
	rm -rf venv
	rm -rf __pycache__

.PHONY: tests all
