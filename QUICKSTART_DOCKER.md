# Docker 快速启动指南

## 前置要求

**注意**：Docker 容器内不需要虚拟环境，容器本身就是隔离环境。

1. **确保 Docker 网络存在**
```bash
# 如果还没有创建网络，先启动 assistant_account 服务创建网络
cd ../assistant_account
docker compose up -d mysql
```

## 启动服务

### 方式一：使用 Makefile（推荐）

```bash
cd assistant_ai
make docker-run
```

### 方式二：使用 docker-compose

```bash
cd assistant_ai
docker compose up -d --build
```

## 查看日志

```bash
make logs
# 或
docker compose logs -f app
```

## 测试服务

```bash
# 列出可用 Agent
grpcurl -plaintext localhost:50052 ai.v1.AIService/ListAgents

# 发送处理请求
grpcurl -plaintext \
  -d '{"user_id":"user123","message":"Hello, AI!"}' \
  localhost:50052 ai.v1.AIService/Process
```

## 停止服务

```bash
make stop
# 或
docker compose stop
```

## 配置本地模型（Ollama/LocalAI）

如果 Ollama 或其他本地模型服务运行在宿主机上，需要在 Docker 容器中访问：

### 步骤 1：创建 `.env` 文件

在 `assistant_ai` 目录下创建 `.env` 文件：

```bash
cd assistant_ai
cat > .env << 'EOF'
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
OPENAI_MODEL=deepseek-r1:14b
EOF
```

**重要提示**：
- 使用 `host.docker.internal` 而不是 `localhost`，因为容器内的 `localhost` 指向容器本身，而不是宿主机
- 将 `deepseek-r1:14b` 替换为你实际安装的模型名称（可通过 `curl http://localhost:11434/v1/models` 查看）

### macOS/Windows

`.env` 文件配置示例：
```env
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
OPENAI_MODEL=deepseek-r1:14b
```

### Linux

在 Linux 上，可能需要使用宿主机的 IP 地址或配置网络模式：

**方式一**：使用 host.docker.internal（推荐）
```env
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
```

**方式二**：使用宿主机 IP
```bash
# 获取宿主机 IP
ip addr show docker0 | grep inet
# 然后在 .env 中使用该 IP
OPENAI_BASE_URL=http://172.17.0.1:11434/v1
```

**方式三**：使用 host 网络模式（不推荐，会失去网络隔离）
在 `docker-compose.yml` 中添加：
```yaml
network_mode: host
```

## 常见问题

### 问题：容器无法访问宿主机的 Ollama 服务

**症状**：配置了 `http://localhost:11434/v1` 但连接失败，出现 `APIConnectionError`

**解决方案**：

1. **创建 `.env` 文件**（如果不存在）：
   ```bash
   cd assistant_ai
   cat > .env << EOF
   OPENAI_BASE_URL=http://host.docker.internal:11434/v1
   OPENAI_MODEL=deepseek-r1:14b
   EOF
   ```
   注意：将 `deepseek-r1:14b` 替换为你实际安装的模型名称。

2. **验证 Ollama 在宿主机上运行**：
   ```bash
   curl http://localhost:11434/v1/models
   ```

3. **测试容器到宿主机的连接**：
   ```bash
   # 使用测试脚本（推荐）
   ./scripts/test_ollama_connection.sh
   
   # 或手动测试
   docker compose exec app curl http://host.docker.internal:11434/v1/models
   ```

4. **重启容器以应用新配置**：
   ```bash
   docker compose down
   docker compose up -d
   ```

5. **检查日志确认配置已加载**：
   ```bash
   docker compose logs app | grep -i "langchain\|ollama\|base_url"
   ```
   应该看到类似：
   ```
   LangChainAgent configuration - OPENAI_API_KEY: None, OPENAI_BASE_URL: http://host.docker.internal:11434/v1, MODEL: deepseek-r1:14b
   Registered LangChainAgent (ACTIVE) with local model: deepseek-r1:14b at http://host.docker.internal:11434/v1
   ```

**如果仍然失败**：

- **macOS/Windows**：确保 Docker Desktop 设置中启用了 "Allow connections from containers to host"
- **Linux**：可能需要使用宿主机 IP 而不是 `host.docker.internal`：
  ```bash
  # 获取宿主机 IP
  ip addr show docker0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
  # 然后在 .env 中使用该 IP
  OPENAI_BASE_URL=http://172.17.0.1:11434/v1
  ```

### 问题：容器启动失败，提示找不到 protobuf 代码

**解决方案**：
1. 检查依赖是否正确安装：
```bash
docker compose exec app pip list | grep assistant
```

2. 重新构建镜像（会从 Git 仓库安装依赖）：
```bash
docker compose build --no-cache
docker compose up -d
```

### 问题：无法连接到服务

**检查**：
1. 端口是否映射正确：
```bash
docker compose ps
```

2. 服务是否正常运行：
```bash
docker compose logs app
```

3. 网络是否正确：
```bash
docker network inspect assistant_assistant-net
```

## 与 Gateway 集成

服务启动后，可以通过 Gateway 访问：

```bash
# 通过 Gateway 调用
curl -X POST http://localhost:8080/v1/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, AI!"
  }'
```

确保 Gateway 已配置 AI 服务路由（参考 `GATEWAY_INTEGRATION.md`）。

