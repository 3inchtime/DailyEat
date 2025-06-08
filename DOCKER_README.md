# Daily Eat Docker 部署指南

本项目支持使用Docker进行容器化部署，包含前端、后端和数据库三个独立容器。

## 🏗️ 架构概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Vue.js)      │    │   (Django)      │    │   (MySQL)       │
│   Nginx:80      │◄──►│   Port:8000     │◄──►│   Port:3306     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd daily_eat
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（重要！）
nano .env
```

### 3. 一键部署

**Linux/macOS:**
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

**Windows:**
```cmd
docker-deploy.bat
```

### 4. 访问应用
- 前端应用: http://localhost
- 后端API: http://localhost:8000
- 管理后台: http://localhost:8000/admin
- API文档: http://localhost:8000/docs

## 🔧 管理命令

### 基本操作
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 使用管理脚本 (Linux/macOS)
```bash
chmod +x docker-manage.sh

# 启动服务
./docker-manage.sh start

# 查看日志
./docker-manage.sh logs

# 进入后端容器
./docker-manage.sh shell

# 运行数据库迁移
./docker-manage.sh migrate

# 查看所有命令
./docker-manage.sh help
```

## 🏭 生产环境部署

### 1. 使用生产配置
```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 或使用部署脚本选择生产模式
./docker-deploy.sh
```

### 2. 重要的生产环境配置

编辑 `.env` 文件：
```env
# 数据库密码（必须修改）
DB_PASSWORD=your_secure_database_password
DB_ROOT_PASSWORD=your_secure_root_password

# Django密钥（必须修改）
SECRET_KEY=your-very-long-and-random-secret-key

# 域名配置
DOMAIN=yourdomain.com

# 调试模式（生产环境必须为False）
DEBUG=False
```

### 3. SSL/HTTPS 配置

如需HTTPS，请修改 `frontend/nginx.conf` 添加SSL配置：
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... 其他配置
}
```

## 📊 容器详情

### Frontend Container
- **基础镜像**: nginx:alpine
- **端口**: 80 (HTTP), 443 (HTTPS)
- **功能**: 
  - 提供Vue.js静态文件
  - 反向代理API请求到后端
  - Gzip压缩
  - 静态文件缓存

### Backend Container
- **基础镜像**: python:3.11-slim
- **端口**: 8000
- **功能**:
  - Django REST API
  - 自动数据库迁移
  - 静态文件收集
  - Swagger API文档

### Database Container
- **基础镜像**: mysql:8.0
- **端口**: 3306
- **功能**:
  - MySQL数据库
  - 数据持久化
  - 自动初始化脚本

## 🔒 安全考虑

### 生产环境安全检查清单
- [ ] 修改默认数据库密码
- [ ] 设置强密码的Django SECRET_KEY
- [ ] 配置正确的ALLOWED_HOSTS
- [ ] 启用HTTPS
- [ ] 定期备份数据库
- [ ] 监控容器资源使用
- [ ] 更新容器镜像

## 🛠️ 故障排除

### 常见问题

**1. 容器启动失败**
```bash
# 查看详细日志
docker-compose logs [service_name]

# 检查容器状态
docker-compose ps
```

**2. 数据库连接失败**
```bash
# 检查数据库容器是否健康
docker-compose exec database mysqladmin ping

# 检查网络连接
docker-compose exec backend ping database
```

**3. 前端无法访问后端API**
```bash
# 检查nginx配置
docker-compose exec frontend nginx -t

# 查看nginx日志
docker-compose logs frontend
```

**4. 重置所有数据**
```bash
# 停止并删除所有容器和卷
docker-compose down -v

# 重新启动
docker-compose up -d
```

## 📈 性能优化

### 生产环境优化建议
1. **使用Gunicorn**: 生产配置已包含
2. **数据库优化**: 调整MySQL配置
3. **静态文件CDN**: 配置CDN加速
4. **容器资源限制**: 设置内存和CPU限制
5. **日志轮转**: 配置日志轮转策略

### 资源限制示例
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## 🔄 数据备份与恢复

### 备份数据库
```bash
# 使用管理脚本
./docker-manage.sh backup

# 手动备份
docker-compose exec database mysqldump -u daily_eat_user -p daily_eat_db > backup.sql
```

### 恢复数据库
```bash
# 使用管理脚本
./docker-manage.sh restore backup.sql

# 手动恢复
docker-compose exec -T database mysql -u daily_eat_user -p daily_eat_db < backup.sql
```

## 📞 支持

如遇到问题，请检查：
1. Docker和Docker Compose版本
2. 系统资源是否充足
3. 端口是否被占用
4. 环境变量配置是否正确

更多帮助请查看项目文档或提交Issue。
