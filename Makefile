# Image name and default tag
IMAGE_NAME := assistant-ai
IMAGE_TAG  ?= latest
COMPOSE_PROJECT_NAME ?= assistant

# Install Python dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev: install
	pip install -r requirements-dev.txt || true

# Run locally
run:
	python -m cmd.server.main

# Build Docker image
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Build and push to registry (if needed)
push: build
	@echo "Push image: docker push $(IMAGE_NAME):$(IMAGE_TAG)"

# Run with docker-compose
docker-run:
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

.PHONY: install install-dev run build push docker-run logs stop down clean

