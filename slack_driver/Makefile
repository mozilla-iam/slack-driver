REGION	:= us-west-2

all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]].*:' Makefile

install-sls:
	npm install

deploy-dev:
	SLS_DEBUG=* STAGE=dev ./node_modules/.bin/sls deploy --region $(REGION) --stage dev

remove-deploy-dev:
	echo "Warning: removing deployement"
	SLS_DEBUG=* STAGE=dev ./node_modules/.bin/sls remove --region $(REGION) --stage dev

python-venv:
	$(shell [ -d venv ] || python3 -m venv venv)
	echo "# Run this in your shell to activate:"
	echo "source venv/bin/activate"
