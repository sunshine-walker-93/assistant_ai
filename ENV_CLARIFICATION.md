# 虚拟环境 vs Docker 容器说明

## 重要区别

### 本地开发 → 使用虚拟环境 ✅

**为什么需要虚拟环境？**
- 隔离项目依赖，避免与系统 Python 包冲突
- 不同项目可以使用不同版本的包
- 保持系统 Python 环境干净

**如何使用：**
```bash
make venv          # 创建虚拟环境
source .venv/bin/activate  # 激活
make install       # 安装依赖
make run           # 运行服务
```

### Docker 容器 → 不需要虚拟环境 ✅

**为什么不需要？**
- Docker 容器本身就是完全隔离的环境
- 每个容器有独立的文件系统和 Python 环境
- 不需要额外的虚拟环境层

**Dockerfile 中：**
```dockerfile
# 直接安装到系统 Python（容器内）
RUN pip install --no-cache-dir --user -r requirements.txt

# 直接运行（不需要激活虚拟环境）
CMD ["python", "-m", "cmd.server.main"]
```

## 总结

| 环境 | 是否需要虚拟环境 | 原因 |
|------|----------------|------|
| 本地开发 | ✅ 需要 | 隔离依赖，避免冲突 |
| Docker 容器 | ❌ 不需要 | 容器本身已隔离 |

## 常见误解

❌ **误解**：Docker 容器内也需要虚拟环境
✅ **正确**：容器本身就是隔离环境，不需要虚拟环境

❌ **误解**：虚拟环境是为了部署
✅ **正确**：虚拟环境只用于本地开发

