all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]].*:' Makefile

install-sls:
	npm install

deploy-dev:
	SLS_DEBUG=* STAGE=dev ./node_modules/.bin/sls deploy
