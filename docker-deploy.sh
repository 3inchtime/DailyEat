#!/bin/bash

# Daily Eat Docker部署脚本

set -e

echo "=========================================="
echo "    Daily Eat Docker 部署脚本"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建环境变量文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件设置生产环境密码和配置"
    echo "   特别是 SECRET_KEY 和数据库密码"
fi

# 选择部署模式
echo ""
echo "请选择部署模式："
echo "1) 开发环境 (development)"
echo "2) 生产环境 (production)"
read -p "请输入选择 (1-2): " choice

case $choice in
    1)
        echo "🚀 启动开发环境..."
        docker-compose up --build -d
        ;;
    2)
        echo "🚀 启动生产环境..."
        docker-compose -f docker-compose.prod.yml up --build -d
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
if [ $choice -eq 1 ]; then
    docker-compose ps
else
    docker-compose -f docker-compose.prod.yml ps
fi

echo ""
echo "=========================================="
echo "           🎉 部署完成！"
echo "=========================================="
echo ""
echo "📍 访问地址:"
echo "   前端应用: http://localhost"
echo "   后端API: http://localhost:8000"
echo "   管理后台: http://localhost:8000/admin"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "👤 默认账户:"
echo "   用户名: admin"
echo "   密码: admin"
echo ""
echo "🔧 管理命令:"
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
