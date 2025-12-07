#!/bin/bash
# Test script to verify Ollama connection from Docker container

set -e

echo "=== Testing Ollama Connection from Docker Container ==="
echo ""

# Check if container is running
if ! docker compose ps | grep -q "assistant-ai-app.*Up"; then
    echo "❌ Container is not running. Please start it first:"
    echo "   docker compose up -d"
    exit 1
fi

echo "1. Testing connection to host.docker.internal:11434..."
if docker compose exec -T app curl -s -f --max-time 5 http://host.docker.internal:11434/v1/models > /dev/null 2>&1; then
    echo "✅ Successfully connected to Ollama via host.docker.internal"
    echo ""
    echo "Available models:"
    docker compose exec -T app curl -s http://host.docker.internal:11434/v1/models | python3 -m json.tool 2>/dev/null || docker compose exec -T app curl -s http://host.docker.internal:11434/v1/models
else
    echo "❌ Failed to connect to Ollama via host.docker.internal:11434"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Verify Ollama is running on host:"
    echo "     curl http://localhost:11434/v1/models"
    echo ""
    echo "  2. Check if host.docker.internal resolves:"
    docker compose exec -T app ping -c 1 host.docker.internal 2>&1 || echo "     ping failed"
    echo ""
    echo "  3. Try alternative: Use host IP address"
    echo "     Get host IP: ipconfig getifaddr en0 (macOS) or ip addr show docker0 (Linux)"
    exit 1
fi

echo ""
echo "2. Checking environment variables in container..."
echo "OPENAI_BASE_URL:"
docker compose exec -T app printenv OPENAI_BASE_URL || echo "  (not set)"
echo "OPENAI_MODEL:"
docker compose exec -T app printenv OPENAI_MODEL || echo "  (not set)"
echo ""

echo "3. Testing with current configuration..."
if [ -n "$(docker compose exec -T app printenv OPENAI_BASE_URL)" ]; then
    BASE_URL=$(docker compose exec -T app printenv OPENAI_BASE_URL)
    echo "Current OPENAI_BASE_URL: $BASE_URL"
    
    # Extract host and port
    if [[ $BASE_URL =~ http://([^:]+):([0-9]+) ]]; then
        HOST="${BASH_REMATCH[1]}"
        PORT="${BASH_REMATCH[2]}"
        echo "Testing connection to $HOST:$PORT..."
        
        if docker compose exec -T app curl -s -f --max-time 5 "http://${HOST}:${PORT}/v1/models" > /dev/null 2>&1; then
            echo "✅ Connection test passed"
        else
            echo "❌ Connection test failed"
            echo "   Please verify the URL is correct and Ollama is accessible"
        fi
    fi
else
    echo "⚠️  OPENAI_BASE_URL is not set"
    echo "   Create a .env file with:"
    echo "   OPENAI_BASE_URL=http://host.docker.internal:11434/v1"
    echo "   OPENAI_MODEL=your-model-name"
fi

echo ""
echo "=== Test Complete ==="

