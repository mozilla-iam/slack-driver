REGION		:= us-west-2
SLS_DEBUG	:= *
PROGNAME	:= slack-driver
PROGDIR		:= slack_driver

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]].*:' Makefile


install:
	@echo Note that installing $(PROGNAME) does not deploy it, it just packages a local copy
	pip install $(PROGNAME)

install-sls: .sls-installed
	touch .sls-installed
	npm install

deploy-prod: install-sls
	SLS_DEBUG=$(SLS_DEBUG) STAGE=prod ./node_modules/.bin/sls deploy --region $(REGION) --stage prod

remove-deploy-prod: install-sls
	echo "Warning: removing deployement"
	SLS_DEBUG=$(SLS_DEBUG) STAGE=prod ./node_modules/.bin/sls remove --region $(REGION) --stage prod

deploy-dev: install-sls
	SLS_DEBUG=$(SLS_DEBUG) STAGE=dev ./node_modules/.bin/sls deploy --region $(REGION) --stage dev

remove-deploy-dev: install-sls
	echo "Warning: removing deployement"
	SLS_DEBUG=$(SLS_DEBUG) STAGE=dev ./node_modules/.bin/sls remove --region $(REGION) --stage dev

python-venv:
	$(shell [ -d venv ] || python3 -m venv venv)
	echo "# Run this in your shell to activate:"
	echo "source venv/bin/activate"

test: tests
tests:
	flake8 setup.py
	flake8 $(PROGDIR)/*.py
	flake8 $(PROGDIR)/tests
	python setup.py test

clean:
	rm -rf node_modules
	rm -rf venv
	rm -rf __pycache__
	rm -rf *.egg-info

.PHONY: test tests clean all
