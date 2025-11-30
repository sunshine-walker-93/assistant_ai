# Docker 部署指南

## 构建和运行

### 方式一：使用 docker-compose（推荐）

1. **确保 assistant_ai_api 已生成代码**

```bash
cd ../assistant_ai_api
make gen-proto
```

2. **构建并启动容器**

```bash
cd ../assistant_ai
make docker-run
# 或
docker compose up -d --build
```

3. **查看日志**

```bash
make logs
# 或
docker compose logs -f app
```

### 方式二：直接使用 Docker

1. **构建镜像**

```bash
docker build -t assistant-ai:latest .
```

2. **运行容器**

```bash
docker run -d \
  --name assistant-ai-app \
  --network assistant_assistant-net \
  -p 50052:50052 \
  -v $(pwd)/../assistant_ai_api/python:/app/assistant_ai_api/python:ro \
  -e GRPC_ADDR=0.0.0.0:50052 \
  assistant-ai:latest
```

## 重要说明

### Volume 挂载

`assistant_ai_api` 的生成代码通过 volume 挂载到容器中：

```yaml
volumes:
  - ../assistant_ai_api/python:/app/assistant_ai_api/python:ro
```

这确保：
- 代码更新后无需重新构建镜像
- 生成的 protobuf 代码始终是最新的

### 网络配置

容器需要加入 `assistant_assistant-net` 网络，以便与其他服务（如 Gateway）通信。

### 环境变量

- `GRPC_ADDR`: gRPC 监听地址（默认: `0.0.0.0:50052`）
- `LOG_LEVEL`: 日志级别（默认: `INFO`）
- `OPENAI_API_KEY`: OpenAI API 密钥（可选）
- `ANTHROPIC_API_KEY`: Anthropic API 密钥（可选）

## 故障排查

### 问题：容器启动失败

1. **检查日志**
```bash
docker compose logs app
```

2. **检查 protobuf 代码是否存在**
```bash
docker compose exec app ls -la /app/assistant_ai_api/python/pb/ai/v1/
```

3. **检查 Python 路径**
```bash
docker compose exec app python -c "import sys; print(sys.path)"
```

### 问题：无法连接到服务

1. **检查端口映射**
```bash
docker compose ps
netstat -an | grep 50052
```

2. **检查网络**
```bash
docker network inspect assistant_assistant-net
```

3. **测试连接**
```bash
grpcurl -plaintext localhost:50052 ai.v1.AIService/ListAgents
```

