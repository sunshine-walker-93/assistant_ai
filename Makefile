# Image name and default tag
IMAGE_NAME := assistant-ai
IMAGE_TAG  ?= latest
COMPOSE_PROJECT_NAME ?= assistant

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source .venv/bin/activate"

# Install Python dependencies (in virtual environment if exists)
install: venv-check install-api
	$(PIP) install -r requirements.txt

# Install assistant_ai_api from GitHub
install-api:
	@echo "Installing assistant_ai_api from GitHub..."
	@chmod +x scripts/install_api.sh 2>/dev/null || true
	@bash scripts/install_api.sh || \
	 (echo "Warning: Could not install via script, trying alternative method..." && \
	  $(MAKE) install-api-alt)

# Alternative installation method
install-api-alt:
	@echo "Using alternative installation method..."
	@rm -rf /tmp/assistant_ai_api_install
	@mkdir -p /tmp/assistant_ai_api_install
	@cd /tmp/assistant_ai_api_install && \
	 git clone --depth 1 https://github.com/sunshine-walker-93/assistant_ai_api.git . && \
	 if [ -d python ]; then \
	   SITE_PACKAGES=$$($(PYTHON) -c "import site; print(site.getsitepackages()[0])"); \
	   echo "$$(pwd)/python" > $$SITE_PACKAGES/assistant_ai_api.pth; \
	   echo "Installed to $$SITE_PACKAGES/assistant_ai_api.pth"; \
	 else \
	   echo "Error: python directory not found"; \
	   exit 1; \
	 fi

# Install development dependencies
install-dev: install
	$(PIP) install -r requirements-dev.txt || true

# Check if virtual environment exists, create if not
venv-check:
	@if [ ! -d .venv ]; then \
		echo "Virtual environment not found. Creating one..."; \
		$(MAKE) venv; \
	fi

# Detect pip command (use venv pip if available)
PIP := $(shell if [ -f .venv/bin/pip ]; then echo .venv/bin/pip; else echo pip3; fi)
PYTHON := $(shell if [ -f .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

# Run locally (use venv python if available)
run:
	$(PYTHON) -m cmd.server.main

# Build Docker image
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Build and push to registry (if needed)
push: build
	@echo "Push image: docker push $(IMAGE_NAME):$(IMAGE_TAG)"

# Run with docker-compose
docker-run:
	@echo "Building and starting AI service..."
	@echo "Note: Ensure assistant_ai_api/python exists (run 'make gen-proto' in assistant_ai_api)"
	docker compose -p $(COMPOSE_PROJECT_NAME) up -d --build app

# View logs
logs:
	docker compose -p $(COMPOSE_PROJECT_NAME) logs -f app

# Stop containers
stop:
	docker compose -p $(COMPOSE_PROJECT_NAME) stop app

# Remove containers
down:
	docker compose -p $(COMPOSE_PROJECT_NAME) down

# Clean Python cache
clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

.PHONY: venv venv-check install install-dev run build push docker-run logs stop down clean

