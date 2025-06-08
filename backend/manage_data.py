#!/usr/bin/env python3
"""
统一的数据管理脚本
整合了数据库创建、食物数据导入、测试数据创建等功能
"""
import os
import sys
import django
from datetime import datetime, date, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily_eat_backend.settings')
django.setup()

from daily_eat.models import MealLogs, Foods
from django.contrib.auth.models import User
from django.utils import timezone

class DataManager:
    def __init__(self):
        pass
    
    def create_test_user(self, username="fooduser", password="12345678"):
        """创建测试用户"""
        print(f"👤 创建测试用户: {username}")
        
        try:
            user = User.objects.get(username=username)
            print(f"✅ 用户 {username} 已存在")
            return user
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f"{username}@example.com"
            )
            print(f"✅ 用户 {username} 创建成功")
            return user
    
    def import_food_data(self, csv_file="food.csv"):
        """导入食物数据"""
        print(f"🍎 导入食物数据: {csv_file}")
        
        if not os.path.exists(csv_file):
            print(f"❌ 文件不存在: {csv_file}")
            return False
        
        import csv
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                created_count = 0
                updated_count = 0
                
                for row in reader:
                    # 解析餐次适用性
                    meal_types = row.get('meal_types', '').split(',')
                    
                    food_data = {
                        'name': row['name'],
                        'description': row.get('description', ''),
                        'calories': int(row['calories']) if row.get('calories') else None,
                        'image_url': row.get('image_url', ''),
                        'tags': row.get('tags', ''),
                        'is_for_breakfast': '早餐' in meal_types,
                        'is_for_lunch': '中餐' in meal_types,
                        'is_for_afternoon_tea': '下午茶' in meal_types,
                        'is_for_dinner': '晚餐' in meal_types,
                        'is_for_supper': '夜宵' in meal_types,
                    }
                    
                    food, created = Foods.objects.get_or_create(
                        name=row['name'],
                        defaults=food_data
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # 更新现有食物
                        for key, value in food_data.items():
                            setattr(food, key, value)
                        food.save()
                        updated_count += 1
                
                print(f"✅ 食物数据导入完成: 新增 {created_count} 个，更新 {updated_count} 个")
                return True
                
        except Exception as e:
            print(f"❌ 导入食物数据失败: {e}")
            return False
    
    def create_test_meal_logs(self, username="fooduser", days=7):
        """创建测试用餐记录"""
        print(f"🍽️ 为用户 {username} 创建 {days} 天的测试用餐记录")
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"❌ 用户 {username} 不存在")
            return False
        
        # 获取食物
        foods = Foods.objects.all()[:10]
        if not foods:
            print("❌ 没有找到食物数据，请先导入食物数据")
            return False
        
        # 删除现有记录
        existing_count = MealLogs.objects.filter(user=user).count()
        if existing_count > 0:
            MealLogs.objects.filter(user=user).delete()
            print(f"🗑️ 删除了 {existing_count} 条现有记录")
        
        # 创建新记录
        meal_types = ['早餐', '中餐', '晚餐', '下午茶', '夜宵']
        created_count = 0
        
        for i in range(days):
            current_date = date.today() - timedelta(days=i)
            
            # 每天创建2-4条记录
            meals_per_day = 3 if i < 3 else 2  # 最近3天多一些记录
            
            for j in range(meals_per_day):
                food = foods[j % len(foods)]
                meal_type = meal_types[j % len(meal_types)]
                
                # 创建时间戳
                hour = 8 + j * 4  # 8点、12点、16点、20点
                naive_time = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                eaten_time = timezone.make_aware(naive_time)
                
                MealLogs.objects.create(
                    user=user,
                    food=food,
                    meal_type_recorded=meal_type,
                    eaten_at_datetime=eaten_time
                )
                created_count += 1
        
        print(f"✅ 成功创建 {created_count} 条用餐记录")
        
        # 显示统计
        total_calories = sum(log.food.calories or 0 for log in MealLogs.objects.filter(user=user))
        print(f"📊 总热量: {total_calories} kcal")
        
        return True
    
    def reset_database(self):
        """重置数据库（清空所有数据）"""
        print("🔄 重置数据库...")
        
        confirm = input("⚠️  这将删除所有数据，确认吗？(y/N): ")
        if confirm.lower() != 'y':
            print("❌ 操作已取消")
            return False
        
        try:
            # 删除用餐记录
            meal_count = MealLogs.objects.count()
            MealLogs.objects.all().delete()
            print(f"🗑️ 删除了 {meal_count} 条用餐记录")
            
            # 删除食物（保留超级用户创建的）
            food_count = Foods.objects.count()
            Foods.objects.all().delete()
            print(f"🗑️ 删除了 {food_count} 种食物")
            
            # 删除普通用户（保留超级用户）
            user_count = User.objects.filter(is_superuser=False).count()
            User.objects.filter(is_superuser=False).delete()
            print(f"🗑️ 删除了 {user_count} 个普通用户")
            
            print("✅ 数据库重置完成")
            return True
            
        except Exception as e:
            print(f"❌ 重置数据库失败: {e}")
            return False
    
    def show_stats(self):
        """显示数据库统计信息"""
        print("\n📊 数据库统计信息")
        print("="*30)
        
        user_count = User.objects.count()
        food_count = Foods.objects.count()
        meal_count = MealLogs.objects.count()
        
        print(f"👤 用户数量: {user_count}")
        print(f"🍎 食物数量: {food_count}")
        print(f"🍽️ 用餐记录: {meal_count}")
        
        if User.objects.exists():
            print("\n👤 用户列表:")
            for user in User.objects.all():
                user_meals = MealLogs.objects.filter(user=user).count()
                print(f"   - {user.username}: {user_meals} 条用餐记录")

def main():
    """主函数"""
    manager = DataManager()
    
    if len(sys.argv) < 2:
        print("数据管理工具")
        print("用法: python manage_data.py <command> [options]")
        print("\n可用命令:")
        print("  create-user [username] [password]  - 创建测试用户")
        print("  import-foods [csv_file]           - 导入食物数据")
        print("  create-meals [username] [days]    - 创建测试用餐记录")
        print("  reset                             - 重置数据库")
        print("  stats                             - 显示统计信息")
        print("  setup                             - 完整设置（用户+食物+用餐记录）")
        return
    
    command = sys.argv[1]
    
    if command == "create-user":
        username = sys.argv[2] if len(sys.argv) > 2 else "fooduser"
        password = sys.argv[3] if len(sys.argv) > 3 else "12345678"
        manager.create_test_user(username, password)
    
    elif command == "import-foods":
        csv_file = sys.argv[2] if len(sys.argv) > 2 else "food.csv"
        manager.import_food_data(csv_file)
    
    elif command == "create-meals":
        username = sys.argv[2] if len(sys.argv) > 2 else "fooduser"
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        manager.create_test_meal_logs(username, days)
    
    elif command == "reset":
        manager.reset_database()
    
    elif command == "stats":
        manager.show_stats()
    
    elif command == "setup":
        print("🚀 开始完整设置...")
        manager.create_test_user()
        manager.import_food_data()
        manager.create_test_meal_logs()
        manager.show_stats()
        print("🎉 设置完成！")
    
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()
