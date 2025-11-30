# 安装脚本说明

## install_api.sh

用于从 GitHub 仓库安装 `assistant_ai_api` 的脚本。

### 使用方法

```bash
# 在虚拟环境中运行
source .venv/bin/activate
./scripts/install_api.sh
```

### 工作原理

1. 克隆 `assistant_ai_api` 仓库到临时目录
2. 找到 `python` 子目录
3. 创建 `.pth` 文件添加到 Python 路径
4. 清理临时文件

### 注意

这是一个临时解决方案。更好的方式是在 `assistant_ai_api` 仓库的 `python` 目录添加 `setup.py`，这样就可以直接通过 pip 安装。

## 建议：在 assistant_ai_api 添加 setup.py

在 `assistant_ai_api/python` 目录创建 `setup.py`：

```python
from setuptools import setup, find_packages

setup(
    name="assistant-ai-api",
    version="1.0.0",
    description="Assistant AI API Protocol Buffer definitions",
    packages=find_packages(),
    python_requires=">=3.11",
)
```

然后就可以在 `requirements.txt` 中使用：
```
git+https://github.com/sunshine-walker-93/assistant_ai_api.git#subdirectory=python
```

