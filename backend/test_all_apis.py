#!/usr/bin/env python3
"""
统一的后端API测试脚本
整合了所有API测试功能
"""
import requests
import json
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {}
        
    def login(self, username="fooduser", password="12345678"):
        """登录获取token"""
        print(f"\n🔐 登录用户: {username}")
        login_data = {"username": username, "password": password}
        
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data.get('access')
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return False
    
    def test_auth_apis(self):
        """测试认证相关API"""
        print("\n" + "="*50)
        print("🔐 测试认证API")
        print("="*50)
        
        # 测试获取用户信息
        response = requests.get(f"{BASE_URL}/auth/me/", headers=self.headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 获取用户信息成功: {user_data.get('username')}")
        else:
            print(f"❌ 获取用户信息失败: {response.status_code}")
    
    def test_foods_apis(self):
        """测试食物相关API"""
        print("\n" + "="*50)
        print("🍎 测试食物API")
        print("="*50)
        
        # 获取食物列表
        response = requests.get(f"{BASE_URL}/foods/", headers=self.headers)
        if response.status_code == 200:
            foods_data = response.json()
            if isinstance(foods_data, dict) and 'results' in foods_data:
                foods = foods_data['results']
            else:
                foods = foods_data
            print(f"✅ 获取食物列表成功: {len(foods)} 种食物")
            
            # 显示前3种食物
            for i, food in enumerate(foods[:3]):
                print(f"   {i+1}. {food.get('name')} - {food.get('calories')}kcal")
        else:
            print(f"❌ 获取食物列表失败: {response.status_code}")
        
        # 测试食物推荐
        response = requests.get(f"{BASE_URL}/foods/suggest/", 
                              params={"meal_type": "早餐"}, 
                              headers=self.headers)
        if response.status_code == 200:
            suggestions = response.json()
            print(f"✅ 早餐推荐成功: {len(suggestions)} 种食物")
        else:
            print(f"❌ 食物推荐失败: {response.status_code}")
    
    def test_meal_logs_apis(self):
        """测试用餐记录API"""
        print("\n" + "="*50)
        print("🍽️ 测试用餐记录API")
        print("="*50)
        
        # 获取用餐记录
        response = requests.get(f"{BASE_URL}/meal-logs/", headers=self.headers)
        if response.status_code == 200:
            logs_data = response.json()
            if isinstance(logs_data, dict) and 'results' in logs_data:
                logs = logs_data['results']
            else:
                logs = logs_data
            print(f"✅ 获取用餐记录成功: {len(logs)} 条记录")
            
            # 显示最近3条记录
            for i, log in enumerate(logs[:3]):
                food_detail = log.get('food_detail', {})
                food_name = food_detail.get('name') if food_detail else 'Unknown'
                print(f"   {i+1}. {food_name} - {log.get('meal_type_recorded')} - {log.get('eaten_at_datetime')}")
        else:
            print(f"❌ 获取用餐记录失败: {response.status_code}")
    
    def test_stats_apis(self):
        """测试统计API"""
        print("\n" + "="*50)
        print("📊 测试统计API")
        print("="*50)
        
        # 测试每日统计
        today = date.today().strftime('%Y-%m-%d')
        response = requests.get(f"{BASE_URL}/stats/daily-calories/", 
                              params={"date": today}, 
                              headers=self.headers)
        
        if response.status_code == 200:
            daily_stats = response.json()
            print(f"✅ 每日统计API成功")
            print(f"   日期: {daily_stats.get('date')}")
            print(f"   总热量: {daily_stats.get('total_calories_consumed')}kcal")
            print(f"   目标热量: {daily_stats.get('target_calories')}")
            print(f"   餐次分布: {daily_stats.get('breakdown_by_meal_type')}")
        else:
            print(f"❌ 每日统计API失败: {response.status_code}")
        
        # 测试周统计
        response = requests.get(f"{BASE_URL}/stats/weekly/", headers=self.headers)
        if response.status_code == 200:
            weekly_stats = response.json()
            print(f"✅ 周统计API成功")
            print(f"   时间范围: {weekly_stats.get('start_date')} 到 {weekly_stats.get('end_date')}")
            print(f"   总热量: {weekly_stats.get('total_calories')}kcal")
            print(f"   总用餐次数: {weekly_stats.get('total_meals')}次")
            print(f"   平均每日热量: {weekly_stats.get('avg_daily_calories')}kcal")
        else:
            print(f"❌ 周统计API失败: {response.status_code}")
    
    def test_goals_apis(self):
        """测试目标管理API"""
        print("\n" + "="*50)
        print("🎯 测试目标管理API")
        print("="*50)
        
        # 获取热量目标
        response = requests.get(f"{BASE_URL}/goals/daily-calorie/", headers=self.headers)
        if response.status_code == 200:
            goal_data = response.json()
            print(f"✅ 获取热量目标成功: {goal_data.get('target_calories')}kcal")
        else:
            print(f"❌ 获取热量目标失败: {response.status_code}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始API全面测试...")
        
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            return
        
        self.test_auth_apis()
        self.test_foods_apis()
        self.test_meal_logs_apis()
        self.test_stats_apis()
        self.test_goals_apis()
        
        print("\n" + "="*50)
        print("🎉 所有API测试完成！")
        print("="*50)

def main():
    """主函数"""
    import sys
    
    tester = APITester()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "auth":
            if tester.login():
                tester.test_auth_apis()
        elif test_type == "foods":
            if tester.login():
                tester.test_foods_apis()
        elif test_type == "meals":
            if tester.login():
                tester.test_meal_logs_apis()
        elif test_type == "stats":
            if tester.login():
                tester.test_stats_apis()
        elif test_type == "goals":
            if tester.login():
                tester.test_goals_apis()
        else:
            print("用法: python test_all_apis.py [auth|foods|meals|stats|goals]")
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()
