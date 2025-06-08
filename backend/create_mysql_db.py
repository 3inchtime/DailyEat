#!/usr/bin/env python3
"""
创建MySQL数据库的脚本
"""
import pymysql
import sys

def create_database(reset=False):
    try:
        # 连接到MySQL服务器（不指定数据库）
        print("🔗 连接到MySQL服务器...")
        connection = pymysql.connect(
            host='localhost',
            user='test',
            password='12345678',
            port=3306
        )

        cursor = connection.cursor()

        if reset:
            # 重置数据库（删除后重新创建）
            print("🗑️ 删除现有数据库...")
            cursor.execute("DROP DATABASE IF EXISTS daily_eat_db")
            print("📊 重新创建数据库 daily_eat_db...")
        else:
            # 创建数据库
            print("📊 创建数据库 daily_eat_db...")

        cursor.execute("CREATE DATABASE IF NOT EXISTS daily_eat_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # 检查数据库是否创建成功
        cursor.execute("SHOW DATABASES LIKE 'daily_eat_db'")
        result = cursor.fetchone()
        
        if result:
            print("✅ 数据库 daily_eat_db 创建成功！")
        else:
            print("❌ 数据库创建失败")
            return False
            
        # 显示数据库信息
        cursor.execute("SELECT DATABASE()")
        cursor.execute("USE daily_eat_db")
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()
        print(f"📍 当前数据库: {current_db[0] if current_db and current_db[0] else 'None'}")
        
        cursor.close()
        connection.close()
        
        print("🎉 MySQL数据库配置完成！")
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    # 检查是否有重置参数
    reset = len(sys.argv) > 1 and sys.argv[1] == "--reset"
    success = create_database(reset=reset)
    sys.exit(0 if success else 1)
