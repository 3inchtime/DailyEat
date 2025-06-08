#!/bin/bash

# Daily Eat Docker管理脚本

set -e

show_help() {
    echo "Daily Eat Docker 管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start       启动所有服务"
    echo "  stop        停止所有服务"
    echo "  restart     重启所有服务"
    echo "  logs        查看日志"
    echo "  status      查看服务状态"
    echo "  shell       进入后端容器shell"
    echo "  migrate     运行数据库迁移"
    echo "  collectstatic 收集静态文件"
    echo "  backup      备份数据库"
    echo "  restore     恢复数据库"
    echo "  clean       清理未使用的Docker资源"
    echo "  rebuild     重新构建并启动"
    echo "  help        显示此帮助信息"
}

case "$1" in
    start)
        echo "🚀 启动服务..."
        docker-compose up -d
        ;;
    stop)
        echo "⏹️  停止服务..."
        docker-compose down
        ;;
    restart)
        echo "🔄 重启服务..."
        docker-compose restart
        ;;
    logs)
        echo "📋 查看日志..."
        docker-compose logs -f
        ;;
    status)
        echo "📊 服务状态..."
        docker-compose ps
        ;;
    shell)
        echo "🐚 进入后端容器..."
        docker-compose exec backend bash
        ;;
    migrate)
        echo "🗄️  运行数据库迁移..."
        docker-compose exec backend python manage.py migrate
        ;;
    collectstatic)
        echo "📁 收集静态文件..."
        docker-compose exec backend python manage.py collectstatic --noinput
        ;;
    backup)
        echo "💾 备份数据库..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        docker-compose exec database mysqldump -u daily_eat_user -p daily_eat_db > backup_${timestamp}.sql
        echo "备份完成: backup_${timestamp}.sql"
        ;;
    restore)
        if [ -z "$2" ]; then
            echo "❌ 请指定备份文件"
            echo "用法: $0 restore backup_file.sql"
            exit 1
        fi
        echo "🔄 恢复数据库..."
        docker-compose exec -T database mysql -u daily_eat_user -p daily_eat_db < "$2"
        echo "恢复完成"
        ;;
    clean)
        echo "🧹 清理Docker资源..."
        docker system prune -f
        docker volume prune -f
        ;;
    rebuild)
        echo "🔨 重新构建并启动..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
