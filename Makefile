PYTHON ?= python3

.PHONY: all validate test install init-repo mcp-sync

all: validate test

validate:
	$(PYTHON) scripts/validate.py

test:
	$(PYTHON) -m pytest tests/ -q

install:
	bash scripts/install.sh $(INSTALL_CLIENT)

init-repo:
	$(PYTHON) scripts/init-repo.py $(TARGET) --client $(CLIENT)

mcp-sync:
	$(PYTHON) scripts/mcp-sync.py