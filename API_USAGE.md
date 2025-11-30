# assistant_ai 如何使用 assistant_ai_api

## 概述

`assistant_ai_api` 是一个独立的 GitHub 仓库（[https://github.com/sunshine-walker-93/assistant_ai_api](https://github.com/sunshine-walker-93/assistant_ai_api)），包含 Protocol Buffer 定义和生成的代码。`assistant_ai` 服务通过 pip 从 Git 仓库安装并使用这些 API 定义。

## 架构关系

```
GitHub Repository
└── sunshine-walker-93/assistant_ai_api
    ├── proto/ai/v1/ai.proto      # Protocol Buffer 定义
    └── python/pb/ai/v1/          # 生成的 Python 代码
        ├── ai_pb2.py             # 消息类型定义
        └── ai_pb2_grpc.py        # gRPC 服务定义
            ↓ pip install from Git
assistant_ai/                      # AI 服务实现
├── requirements.txt              # 包含 Git 依赖
└── internal/service/
    └── ai_service.py             # 实现 gRPC 服务接口
```

## 安装方式

### 通过 requirements.txt（推荐）

`requirements.txt` 中已包含：

```txt
git+https://github.com/sunshine-walker-93/assistant_ai_api.git#subdirectory=python
```

安装时自动从 Git 仓库安装：

```bash
pip install -r requirements.txt
```

### 手动安装

```bash
pip install git+https://github.com/sunshine-walker-93/assistant_ai_api.git#subdirectory=python
```

## 使用方式

### 1. 导入生成的代码

```python
# 导入消息类型
from pb.ai.v1 import ai_pb2

# 导入 gRPC 服务接口
from pb.ai.v1 import ai_pb2_grpc

# 使用示例
request = ai_pb2.ProcessRequest(
    user_id="user123",
    message="Hello"
)

response = ai_pb2.ProcessResponse(
    agent_name="simple",
    response="Echo: Hello"
)
```

### 2. 实现 gRPC 服务

在 `internal/service/ai_service.py` 中：

```python
class AIServiceServicer(ai_pb2_grpc.AIServiceServicer):
    """实现 ai_pb2_grpc.AIServiceServicer 接口"""
    
    async def Process(self, request, context):
        # request 是 ai_pb2.ProcessRequest 类型
        message = request.message
        user_id = request.user_id
        
        # 处理逻辑...
        
        # 返回 ai_pb2.ProcessResponse
        return ai_pb2.ProcessResponse(
            agent_name="simple",
            response="Response text"
        )
```

## 优势

1. **版本管理**：通过 Git 标签管理 API 版本
2. **独立部署**：API 定义和实现完全分离
3. **自动安装**：通过 pip 自动安装，无需手动管理路径
4. **一致性**：多个服务可以使用相同版本的 API
5. **简化部署**：Docker 构建时自动安装，无需 volume 挂载

## 工作流程

### 开发流程

1. **修改 API 定义**（在 `assistant_ai_api` 仓库）
   ```bash
   # 编辑 proto/ai/v1/ai.proto
   # 提交并推送到 GitHub
   ```

2. **更新依赖**（在 `assistant_ai` 中）
   ```bash
   # 如果需要特定版本，更新 requirements.txt：
   # git+https://github.com/sunshine-walker-93/assistant_ai_api.git@v1.0.0#subdirectory=python
   
   pip install --upgrade -r requirements.txt
   ```

### 部署流程

1. **构建 Docker 镜像**
   ```bash
   docker build -t assistant-ai:latest .
   ```
   构建时会自动安装 `assistant_ai_api` 依赖

2. **运行容器**
   ```bash
   docker compose up -d
   ```
   无需 volume 挂载，所有依赖已包含在镜像中

## 版本管理

### 使用特定版本

在 `requirements.txt` 中指定版本或标签：

```txt
# 使用特定标签
git+https://github.com/sunshine-walker-93/assistant_ai_api.git@v1.0.0#subdirectory=python

# 使用特定分支
git+https://github.com/sunshine-walker-93/assistant_ai_api.git@main#subdirectory=python

# 使用特定提交
git+https://github.com/sunshine-walker-93/assistant_ai_api.git@abc123#subdirectory=python
```

### 发布新版本

在 `assistant_ai_api` 仓库中：

```bash
git tag v1.0.0
git push origin v1.0.0
```

然后在 `assistant_ai` 的 `requirements.txt` 中更新版本。

## 故障排查

### 问题：ImportError: No module named 'pb'

**原因**：`assistant_ai_api` 未安装

**解决**：
```bash
pip install -r requirements.txt
```

### 问题：安装失败

**检查**：
1. 网络连接是否正常
2. GitHub 仓库是否可访问
3. Git 是否已安装（Docker 中需要）

### 问题：版本不匹配

**解决**：更新 `requirements.txt` 指定正确版本

## 与本地开发的区别

### 之前（本地文件系统）
- 需要本地存在 `assistant_ai_api` 目录
- 需要手动生成 protobuf 代码
- Docker 需要 volume 挂载

### 现在（Git 仓库）
- 直接从 GitHub 安装
- 自动包含生成的代码
- Docker 构建时自动安装
- 更好的版本管理
