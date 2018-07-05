REGION		:= us-west-2
SLS_DEBUG	:= *
PROG_NAME	:= slack-driver
DIR_NAME	:= slack_driver
STAGE		:= dev
SLS_ENV		:= SLS_DEBUG=$(SLS_DEBUG) STAGE=$(STAGE)
SLS_BIN		:= cd $(DIR_NAME) && $(SLS_ENV) ../node_modules/.bin/sls --region $(REGION)

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]].*:' Makefile

install:
	@echo Note that installing $(PROG_NAME) does not deploy it, it just packages a local copy
	pip install $(PROG_NAME)

.install-sls:
	npm install
	touch .install-sls

deploy: .install-sls
	@echo Deploying environment $(STAGE)
	$(SLS_BIN) deploy --stage $(STAGE)

remove-deploy: .install-sls
	echo "Warning: removing deployement $(STAGE)"
	$(SLS_BIN) remove --stage $(STAGE)

python-venv: venv
venv:
	$(shell [ -d venv ] || python3 -m venv venv)
	echo "# Run this in your shell to activate:"
	echo "source venv/bin/activate"

logs:
	$(SLS_BIN) logs --stage $(STAGE) -f $(PROG_NAME)

test: tests
tests:
	flake8 setup.py
	flake8 $(DIR_NAME)/*.py
	flake8 $(DIR_NAME)/tests
	python setup.py test

clean:
	rm -rf node_modules
	rm -rf venv
	rm -rf __pycache__
	rm -rf *.egg-info
	rm -f .install-sls

.PHONY: test tests clean all install
