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

## 常见问题

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

