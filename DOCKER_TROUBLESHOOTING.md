# Docker 构建问题排查

## 问题：镜像拉取失败（401 Unauthorized）

### 原因
Docker 配置了镜像加速器（daocloud.io），但认证失败。

### 解决方案

#### 方案一：临时禁用镜像加速器（推荐）

1. **备份当前配置**
```bash
cp ~/.docker/daemon.json ~/.docker/daemon.json.backup
```

2. **修改配置，移除或替换镜像源**
```bash
cat > ~/.docker/daemon.json <<EOF
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
```

3. **重启 Docker Desktop**
- macOS: 点击 Docker Desktop 图标 → Restart

4. **重新构建**
```bash
make build
```

#### 方案二：使用官方源（最稳定）

```bash
cat > ~/.docker/daemon.json <<EOF
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false
}
EOF
```

然后重启 Docker Desktop。

#### 方案三：手动拉取镜像后构建

```bash
# 先手动拉取镜像（使用官方源）
docker pull python:3.11-slim

# 然后构建
make build
```

### 验证

```bash
# 测试镜像拉取
docker pull python:3.11-slim

# 如果成功，继续构建
make build
```

