# 开发指南

## 虚拟环境设置（仅用于本地开发）

**重要说明**：
- ✅ **本地开发**：使用虚拟环境隔离依赖
- ❌ **Docker 容器**：不需要虚拟环境，容器本身就是隔离环境

强烈建议在本地开发时使用虚拟环境来隔离项目依赖，避免与系统 Python 包的冲突。

### 创建虚拟环境

#### 方式一：使用 Makefile（推荐）

```bash
make venv
source .venv/bin/activate  # macOS/Linux
```

#### 方式二：手动创建

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 安装依赖

虚拟环境激活后：

```bash
# 使用 Makefile（自动检测虚拟环境）
make install

# 或手动安装
pip install -r requirements.txt
```

### 验证虚拟环境

激活虚拟环境后，命令行提示符前会显示 `(.venv)`：

```bash
(.venv) user@host:~/assistant_ai$ python --version
Python 3.11.x
```

### 退出虚拟环境

```bash
deactivate
```

## 开发工作流

### 1. 首次设置

```bash
# 1. 克隆项目（如果还没有）
git clone <repository-url>
cd assistant_ai

# 2. 创建虚拟环境
make venv
source .venv/bin/activate

# 3. 安装依赖
make install

# 4. 运行服务
make run
```

### 2. 日常开发

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行服务
make run

# 或直接运行
python -m cmd.server.main
```

### 3. 添加新依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装新包
pip install <package-name>

# 更新 requirements.txt
pip freeze > requirements.txt
# 或手动添加到 requirements.txt
```

## 虚拟环境的优势

1. **隔离依赖**：避免与系统 Python 包冲突
2. **版本控制**：每个项目可以使用不同版本的包
3. **干净环境**：便于测试和部署
4. **团队协作**：确保团队成员使用相同的依赖版本

## 常见问题

### 问题：虚拟环境未激活

**症状**：安装的包找不到，或使用了系统 Python

**解决**：
```bash
source .venv/bin/activate
```

### 问题：虚拟环境损坏

**解决**：删除并重新创建
```bash
rm -rf .venv
make venv
source .venv/bin/activate
make install
```

### 问题：Docker 构建失败

**注意**：Docker 构建不需要本地虚拟环境，它会创建自己的隔离环境。

## IDE 配置

### VS Code

1. 打开项目
2. 选择 Python 解释器：`Cmd+Shift+P` → "Python: Select Interpreter"
3. 选择 `.venv/bin/python`

### PyCharm

1. File → Settings → Project → Python Interpreter
2. 选择 `.venv/bin/python`

## 最佳实践

1. ✅ **总是使用虚拟环境**进行本地开发
2. ✅ **提交 `.gitignore`**确保虚拟环境不被提交
3. ✅ **定期更新依赖**：`pip install --upgrade -r requirements.txt`
4. ✅ **使用 `requirements.txt`**记录所有依赖
5. ✅ **Docker 构建时**不需要虚拟环境（容器内已隔离）

