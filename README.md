# Assistant AI Service

基于 Python + LangChain/LangGraph 的 AI 智能服务，提供统一入口支持多 Agent 路由和编排。

## 功能特性

- ✅ **统一入口**: 通过 `Process` 方法统一处理用户请求
- ✅ **Agent 注册**: 支持动态注册和管理多个 Agent
- ✅ **智能路由**: 自动路由到合适的 Agent（支持显式指定）
- ✅ **LangGraph 编排**: 支持多 Agent 协作工作流（待实现）
- ✅ **流式响应**: 支持实时流式响应（`ProcessStream`）
- ✅ **gRPC 接口**: 与现有微服务架构一致

## 技术栈

- **Python 3.11+**
- **LangChain**: AI 应用框架
- **LangGraph**: 多 Agent 编排
- **gRPC**: `grpcio`, `grpcio-tools`
- **Protocol Buffers**: API 定义（来自 `assistant_ai_api`）

## 项目结构

```
assistant_ai/
├── cmd/
│   └── server/
│       └── main.py              # gRPC 服务入口
├── internal/
│   ├── agents/                  # Agent 实现
│   │   ├── base.py              # Agent 基类
│   │   ├── registry.py          # Agent 注册中心
│   │   ├── router.py            # 路由策略
│   │   └── simple_agent.py     # 示例 Agent
│   ├── graph/                   # LangGraph 编排
│   │   └── orchestrator.py      # 编排引擎
│   ├── service/                 # gRPC 服务实现
│   │   └── ai_service.py
│   └── config/                  # 配置管理
│       └── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## 快速开始

### 本地开发（使用虚拟环境）

**注意**：虚拟环境仅用于本地开发，Docker 容器不需要虚拟环境。

1. **创建虚拟环境（推荐）**

```bash
# 使用 Makefile（自动创建）
make venv

# 或手动创建
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows
```

2. **安装依赖**

```bash
# 使用 Makefile（自动检测并使用虚拟环境，包含 API 安装）
make install

# 或手动安装（确保已激活虚拟环境）
pip install -r requirements.txt
# 然后安装 assistant_ai_api
python scripts/install_api.sh
```

**注意**：`assistant_ai_api` 目前通过脚本从 GitHub 仓库安装。如果仓库的 `python` 目录添加了 `setup.py`，就可以直接通过 pip 安装。

3. **配置环境变量**

创建 `.env` 文件：
```env
GRPC_ADDR=0.0.0.0:50051
LOG_LEVEL=INFO
OPENAI_API_KEY=your_key_here  # 可选
ANTHROPIC_API_KEY=your_key_here  # 可选
```

4. **运行服务**

```bash
make run
# 或
python -m cmd.server.main
```

### Docker 部署（不需要虚拟环境）

**重要**：Docker 容器本身就是隔离环境，不需要虚拟环境。

1. **构建镜像**

```bash
make build
```

构建时会自动：
- 安装所有 Python 依赖
- 从 GitHub 安装 `assistant_ai_api`

2. **使用 docker-compose**

```bash
make docker-run
```

3. **查看日志**

```bash
make logs
```

## Agent 开发

### 创建新 Agent

1. **继承 BaseAgent**

```python
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
        return "Response"
    
    async def process_stream(self, message: str, context: dict = None):
        # Streaming response
        yield "Response chunk"
```

2. **注册 Agent**

在 `cmd/server/main.py` 中：
```python
from internal.agents.my_agent import MyAgent

my_agent = MyAgent()
registry.register(my_agent)
```

### Agent 扩展说明

**不需要创建新服务！** 所有 Agent 都在同一个 `assistant_ai` 服务中：

- ✅ 添加新 Agent：只需创建新的 Agent 类并注册
- ✅ 动态注册：支持运行时注册（待实现）
- ✅ 独立扩展：如需资源隔离，可考虑独立服务（不推荐）

## API 使用

### 通过 Gateway 调用

Gateway 配置示例：
```yaml
backends:
  - name: "ai"
    addr: "assistant-ai-app:50051"

routes:
  - http_method: "POST"
    http_pattern: "/v1/ai/process"
    backend_name: "ai"
    backend_service: "ai.v1.AIService"
    backend_method: "Process"
    timeout_ms: 30000
```

### 直接 gRPC 调用

```bash
grpcurl -plaintext \
  -d '{"user_id":"user123","message":"Hello"}' \
  localhost:50051 ai.v1.AIService/Process
```

## 配置说明

### 环境变量

- `GRPC_ADDR`: gRPC 监听地址（默认: `0.0.0.0:50051`）
- `LOG_LEVEL`: 日志级别（默认: `INFO`）
- `OPENAI_API_KEY`: OpenAI API 密钥（可选）
- `ANTHROPIC_API_KEY`: Anthropic API 密钥（可选）
- `DEFAULT_AGENT`: 默认 Agent 名称（可选）
- `ENABLE_ORCHESTRATION`: 启用 LangGraph 编排（默认: `false`）

## 开发计划

- [x] 基础框架搭建
- [x] Agent 注册机制
- [x] 简单路由策略
- [ ] LangGraph 集成
- [ ] 语义路由
- [ ] 状态持久化
- [ ] 工具集成（LangChain Tools）

## 与现有架构集成

- ✅ 使用 gRPC 通信，与现有 Go 服务一致
- ✅ 通过 Gateway 统一接入，零代码配置
- ✅ 独立的 API 定义（`assistant_ai_api`）
- ✅ Docker 容器化，加入现有网络
- ✅ 相同的部署和运维模式

## 参考文档

- [开发指南](DEVELOPMENT.md) - 详细的开发环境设置（虚拟环境）
- [快速开始](QUICKSTART.md) - 快速上手指南
- [Docker 部署](QUICKSTART_DOCKER.md) - Docker 部署指南
- [Gateway 集成](GATEWAY_INTEGRATION.md) - Gateway 集成说明
- [API 使用说明](API_USAGE.md) - assistant_ai_api 使用说明

## License

MIT
