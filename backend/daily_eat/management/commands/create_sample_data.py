from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from daily_eat.models import Foods, MealLogs, DailyCalorieGoals
from django.utils import timezone
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = '创建示例数据用于测试'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='demo',
            help='演示用户的用户名'
        )

    def handle(self, *args, **options):
        username = options['username']
        
        # 创建或获取演示用户
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': '演示',
                'last_name': '用户'
            }
        )
        
        if created:
            user.set_password('demo123456')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'创建演示用户: {username}')
            )
        else:
            self.stdout.write(f'使用现有用户: {username}')

        # 创建热量目标
        goal, created = DailyCalorieGoals.objects.get_or_create(
            user=user,
            defaults={'target_calories': 2000}
        )
        if created:
            self.stdout.write('创建每日热量目标: 2000 kcal')

        # 创建示例食物
        sample_foods = [
            {
                'name': '燕麦粥',
                'description': '健康的早餐选择，富含纤维',
                'calories': 150,
                'is_for_breakfast': True,
                'tags': '健康,快手,低卡'
            },
            {
                'name': '鸡胸肉沙拉',
                'description': '高蛋白低脂的午餐',
                'calories': 300,
                'is_for_lunch': True,
                'tags': '健康,高蛋白,减脂'
            },
            {
                'name': '蒸蛋羹',
                'description': '嫩滑的蒸蛋',
                'calories': 120,
                'is_for_breakfast': True,
                'is_for_dinner': True,
                'tags': '简单,营养'
            },
            {
                'name': '红烧肉',
                'description': '经典家常菜',
                'calories': 450,
                'is_for_lunch': True,
                'is_for_dinner': True,
                'tags': '家常,美味'
            },
            {
                'name': '水果沙拉',
                'description': '新鲜水果制作',
                'calories': 80,
                'is_for_afternoon_tea': True,
                'tags': '清爽,维生素'
            },
            {
                'name': '小笼包',
                'description': '上海特色小笼包',
                'calories': 200,
                'is_for_breakfast': True,
                'is_for_supper': True,
                'tags': '传统,美味'
            },
            {
                'name': '青菜豆腐汤',
                'description': '清淡的汤品',
                'calories': 60,
                'is_for_lunch': True,
                'is_for_dinner': True,
                'tags': '清淡,素食'
            },
            {
                'name': '牛肉面',
                'description': '香浓的牛肉面',
                'calories': 400,
                'is_for_lunch': True,
                'is_for_dinner': True,
                'tags': '面食,饱腹'
            }
        ]

        created_foods = []
        for food_data in sample_foods:
            food, created = Foods.objects.get_or_create(
                user=user,
                name=food_data['name'],
                defaults=food_data
            )
            if created:
                created_foods.append(food)

        self.stdout.write(f'创建了 {len(created_foods)} 个示例食物')

        # 创建最近一周的示例用餐记录
        meal_types = ['早餐', '中餐', '晚餐']
        
        for i in range(7):  # 最近7天
            date = timezone.now().date() - timedelta(days=i)
            
            # 每天随机创建2-4个用餐记录
            daily_meals = random.randint(2, 4)
            
            for j in range(daily_meals):
                # 随机选择食物和餐次
                food = random.choice(created_foods)
                meal_type = random.choice(meal_types)
                
                # 设置用餐时间
                if meal_type == '早餐':
                    hour = random.randint(7, 9)
                elif meal_type == '中餐':
                    hour = random.randint(11, 13)
                else:  # 晚餐
                    hour = random.randint(17, 19)
                
                eaten_time = timezone.make_aware(
                    datetime.combine(date, datetime.min.time().replace(
                        hour=hour, 
                        minute=random.randint(0, 59)
                    ))
                )
                
                # 检查是否已存在相同的记录
                if not MealLogs.objects.filter(
                    user=user,
                    food=food,
                    meal_type_recorded=meal_type,
                    eaten_at_datetime__date=date
                ).exists():
                    MealLogs.objects.create(
                        user=user,
                        food=food,
                        meal_type_recorded=meal_type,
                        eaten_at_datetime=eaten_time,
                        notes=f'示例{meal_type}记录'
                    )

        total_logs = MealLogs.objects.filter(user=user).count()
        self.stdout.write(f'创建了用餐记录，用户总记录数: {total_logs}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n示例数据创建完成！\n'
                f'用户名: {username}\n'
                f'密码: demo123456\n'
                f'可以使用这个账户登录并测试API功能。'
            )
        )
