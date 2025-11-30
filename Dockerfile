## Build stage
FROM python:3.11 AS builder

WORKDIR /app

# Install build dependencies
# Use -o Acquire::Check-Valid-Until=false to handle expired repository metadata
RUN apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# Install assistant_ai_api from GitHub
RUN mkdir -p /app/assistant_ai_api && \
    git clone --depth 1 https://github.com/sunshine-walker-93/assistant_ai_api.git /app/assistant_ai_api && \
    if [ -d /app/assistant_ai_api/python ]; then \
      SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])"); \
      echo "/app/assistant_ai_api/python" > $SITE_PACKAGES/assistant_ai_api.pth; \
      echo "Installed assistant_ai_api to $SITE_PACKAGES/assistant_ai_api.pth"; \
    else \
      echo "Error: assistant_ai_api/python directory not found"; \
      exit 1; \
    fi

## Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy assistant_ai_api from builder
COPY --from=builder /app/assistant_ai_api /app/assistant_ai_api

# Create .pth file for assistant_ai_api
RUN SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])") && \
    echo "/app/assistant_ai_api/python" > $SITE_PACKAGES/assistant_ai_api.pth

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Default gRPC address
ENV GRPC_ADDR=0.0.0.0:50051

EXPOSE 50051

# Run the server
CMD ["python", "-m", "cmd.server.main"]
