PYTHON ?= python3
INSTALL_CLIENT ?= claude
CLIENT ?= claude
TARGET ?= ./demo-project
PROJECT ?= .

.PHONY: all validate test install init-repo migrate mcp-sync backlog metrics adoption clean

all: validate test

validate:
	$(PYTHON) scripts/validate.py

test:
	$(PYTHON) -m pytest tests/ -q

install:
	$(PYTHON) scripts/install.py $(INSTALL_CLIENT)

init-repo:
	$(PYTHON) scripts/init-repo.py $(TARGET) --client $(CLIENT)

migrate:
	$(PYTHON) scripts/migrate.py $(TARGET)

mcp-sync:
	$(PYTHON) scripts/mcp-sync.py

backlog:
	$(PYTHON) scripts/backlog.py $(PROJECT)

metrics:
	$(PYTHON) scripts/metrics.py $(PROJECT)

adoption:
	$(PYTHON) scripts/adoption.py

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache build dist *.egg-info
