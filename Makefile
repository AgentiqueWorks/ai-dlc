PYTHON ?= python3

.PHONY: all validate test install

all: validate test

validate:
	$(PYTHON) scripts/validate.py

test:
	$(PYTHON) -m pytest tests/ -q

install:
	bash scripts/install.sh $(INSTALL_CLIENT)