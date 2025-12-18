# Assistant AI Service 快速开始

## 概述

`assistant_ai` 是一个基于 Python + LangChain/LangGraph 的 AI 智能服务，提供统一入口支持多 Agent 路由和编排。

## 架构说明

### 多 Agent 扩展

**重要**：扩展 Agent **不需要**创建新服务！

- ✅ 所有 Agent 都在同一个 `assistant_ai` 服务中
- ✅ 通过 Agent 注册中心动态管理
- ✅ 添加新 Agent：只需创建新的 Agent 类并注册
- ✅ 支持运行时动态注册（待实现）

### 统一入口设计

- 客户端通过统一的 `Process` 方法发送请求
- 服务内部根据消息内容或显式指定路由到合适的 Agent
- 支持 LangGraph 编排多个 Agent 协作（待实现）

## 快速开始

### 1. 创建并激活虚拟环境（推荐）

```bash
# 创建虚拟环境
make venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows
```

**为什么使用虚拟环境？**
- 隔离项目依赖，避免与系统 Python 包冲突
- 便于版本管理和团队协作
- 保持开发环境干净

### 2. 安装依赖

```bash
# 使用 Makefile（自动检测并使用虚拟环境）
make install

# 或手动安装（确保已激活虚拟环境）
pip install -r requirements.txt
```

`assistant_ai_api` 会通过 pip 从 GitHub 仓库自动安装：
- 仓库：https://github.com/sunshine-walker-93/assistant_ai_api
- 自动安装生成的 Python 代码

### 3. 配置环境变量

创建 `.env` 文件：

```env
GRPC_ADDR=0.0.0.0:50052
LOG_LEVEL=INFO
OPENAI_API_KEY=your_key_here  # 可选
ANTHROPIC_API_KEY=your_key_here  # 可选
```

### 4. 运行服务

```bash
# 确保虚拟环境已激活
make run
# 或
python -m cmd.server.main
```

### 5. 测试服务

```bash
# 使用 grpcurl 测试
grpcurl -plaintext \
  -d '{"user_id":"user123","message":"Hello"}' \
  localhost:50052 ai.v1.AIService/Process

# 列出可用 Agent
grpcurl -plaintext \
  localhost:50052 ai.v1.AIService/ListAgents
```

## Docker 部署

### 1. 构建镜像

```bash
make build
```

### 2. 启动服务

```bash
make docker-run
```

### 3. 查看日志

```bash
make logs
```

## Gateway 集成

### 方式一：通过管理 API（推荐）

```bash
# 添加 backend
curl -X POST http://localhost:8080/admin/backends \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ai",
    "addr": "assistant-ai-app:50052"
  }'

# 添加路由
curl -X POST http://localhost:8080/admin/routes \
  -H "Content-Type: application/json" \
  -d '{
    "http_method": "POST",
    "http_pattern": "/v1/ai/process",
    "backend_name": "ai",
    "backend_service": "ai.v1.AIService",
    "backend_method": "Process",
    "timeout_ms": 60000
  }'
```

### 方式二：使用 SQL 脚本

```bash
# 在 MySQL 中执行
mysql -u assistant -p assistant_gateway_db < ../assistant_gateway/db/add_ai_routes.sql
```

### 测试 Gateway 路由

```bash
curl -X POST http://localhost:8080/v1/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, AI!"
  }'
```

## 开发新 Agent

### 1. 创建 Agent 类

```python
# internal/agents/my_agent.py
from internal.agents.base import BaseAgent, AgentMetadata

class MyAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            name="my_agent",
            description="My custom agent",
            capabilities=["feature1", "feature2"]
        )
        super().__init__(metadata)
    
    async def process(self, message: str, context: dict = None) -> str:
        # Your agent logic here
        return "Response from MyAgent"
    
    async def process_stream(self, message: str, context: dict = None):
        # Streaming response
        yield "Response chunk"
```

### 2. 注册 Agent

在 `cmd/server/main.py` 中：

```python
from internal.agents.my_agent import MyAgent

my_agent = MyAgent()
registry.register(my_agent)
```

### 3. 重启服务

```bash
make run
```

## 项目结构

```
assistant_ai/
├── cmd/server/main.py          # 服务入口
├── internal/
│   ├── agents/                 # Agent 实现
│   │   ├── base.py            # Agent 基类
│   │   ├── registry.py        # 注册中心
│   │   ├── router.py          # 路由策略
│   │   └── langchain_agent.py # LangChain Agent
│   ├── graph/                  # LangGraph 编排
│   │   └── orchestrator.py
│   ├── service/                # gRPC 服务
│   │   └── ai_service.py
│   └── config/                 # 配置
│       └── config.py
├── .venv/                      # 虚拟环境（不提交到 Git）
├── requirements.txt
└── Makefile
```

## 下一步

- [ ] 集成 LangChain LLM
- [ ] 实现语义路由
- [ ] 实现 LangGraph 编排
- [ ] 添加状态持久化
- [ ] 集成 LangChain Tools

## 参考文档

- [开发指南](DEVELOPMENT.md) - 详细的开发环境设置
- [Gateway 集成指南](GATEWAY_INTEGRATION.md)
- [API 使用说明](API_USAGE.md)
- [README](README.md)
