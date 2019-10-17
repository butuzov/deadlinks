VERSION := 0.0.1
IMAGE := butuzov/deadlinks

update:
	@echo Update deadlinks version to $(VERSION) ...
	@sed -i 's/^VERSION := .*/VERSION := $(VERSION)/g' Makefile

build:
	docker build -t ${IMAGE}:${VERSION} -t ${IMAGE}:latest  .

push:
	docker push ${IMAGE}:${VERSION}
	docker push ${IMAGE}:latest

