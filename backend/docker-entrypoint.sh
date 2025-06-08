#!/bin/bash

# 等待数据库启动
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database started"

# 运行数据库迁移
echo "Running database migrations..."
python manage.py migrate

# 创建超级用户（如果不存在）
echo "Creating superuser..."
python manage_data.py create-user admin admin || true

# 导入初始数据
echo "Importing initial data..."
python manage_data.py import-foods || true

# 启动应用
echo "Starting application..."
exec "$@"
