# Gateway 集成指南

本文档说明如何将 `assistant_ai` 服务集成到 `assistant_gateway` 中。

## 方式一：通过管理 API（推荐）

### 1. 添加 Backend

```bash
curl -X POST http://localhost:8080/admin/backends \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ai",
    "addr": "assistant-ai-app:50051",
    "description": "AI Service with LangChain/LangGraph agents"
  }'
```

### 2. 添加路由

#### 统一入口路由
```bash
curl -X POST http://localhost:8080/admin/routes \
  -H "Content-Type: application/json" \
  -d '{
    "http_method": "POST",
    "http_pattern": "/v1/ai/process",
    "backend_name": "ai",
    "backend_service": "ai.v1.AIService",
    "backend_method": "Process",
    "timeout_ms": 60000,
    "description": "Unified entry point for AI processing"
  }'
```

#### 流式响应路由
```bash
curl -X POST http://localhost:8080/admin/routes \
  -H "Content-Type: application/json" \
  -d '{
    "http_method": "POST",
    "http_pattern": "/v1/ai/process/stream",
    "backend_name": "ai",
    "backend_service": "ai.v1.AIService",
    "backend_method": "ProcessStream",
    "timeout_ms": 60000,
    "description": "Streaming AI response"
  }'
```

#### Agent 列表路由（管理接口）
```bash
curl -X POST http://localhost:8080/admin/routes \
  -H "Content-Type: application/json" \
  -d '{
    "http_method": "GET",
    "http_pattern": "/v1/ai/agents",
    "backend_name": "ai",
    "backend_service": "ai.v1.AIService",
    "backend_method": "ListAgents",
    "timeout_ms": 5000,
    "description": "List available AI agents"
  }'
```

## 方式二：修改配置文件

编辑 `assistant_gateway/configs/config.yaml` 或 `config.docker.yaml`：

```yaml
backends:
  - name: "account"
    addr: "127.0.0.1:50051"
  - name: "ai"
    addr: "127.0.0.1:50051"  # 本地开发
    # addr: "assistant-ai-app:50051"  # Docker 环境

routes:
  - http_method: "POST"
    http_pattern: "/v1/user/login"
    backend_name: "account"
    backend_service: "user.v1.UserService"
    backend_method: "Login"
    timeout_ms: 1000
  
  # AI Service routes
  - http_method: "POST"
    http_pattern: "/v1/ai/process"
    backend_name: "ai"
    backend_service: "ai.v1.AIService"
    backend_method: "Process"
    timeout_ms: 60000
  
  - http_method: "POST"
    http_pattern: "/v1/ai/process/stream"
    backend_name: "ai"
    backend_service: "ai.v1.AIService"
    backend_method: "ProcessStream"
    timeout_ms: 60000
  
  - http_method: "GET"
    http_pattern: "/v1/ai/agents"
    backend_name: "ai"
    backend_service: "ai.v1.AIService"
    backend_method: "ListAgents"
    timeout_ms: 5000
```

## 测试

### 1. 测试统一入口

```bash
curl -X POST http://localhost:8080/v1/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, AI!"
  }'
```

### 2. 测试显式指定 Agent

```bash
curl -X POST http://localhost:8080/v1/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, AI!",
    "agent_name": "simple"
  }'
```

### 3. 测试 Agent 列表

```bash
curl http://localhost:8080/v1/ai/agents
```

## 注意事项

1. **网络配置**：确保 Gateway 和 AI 服务在同一个 Docker 网络中（`assistant_assistant-net`）
2. **超时设置**：AI 处理可能需要较长时间，建议设置较大的超时值（30-60秒）
3. **流式响应**：Gateway 需要支持 gRPC 流式响应转发（当前实现可能需要验证）
4. **错误处理**：确保 Gateway 能正确处理 AI 服务的错误响应

## 验证清单

- [ ] AI 服务已启动并监听 `:50051`
- [ ] Gateway 已添加 AI 服务 backend
- [ ] Gateway 已配置路由规则
- [ ] 测试统一入口接口
- [ ] 测试 Agent 列表接口
- [ ] 验证错误处理

