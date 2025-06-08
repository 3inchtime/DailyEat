"""
Django管理命令：导入食物数据到数据库

使用方法：
python manage.py import_foods --file foods_data.json --user username
python manage.py import_foods --file foods_data.csv --user username
python manage.py import_foods --create-user testuser --file foods_data.json
"""

import json
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from daily_eat.models import Foods


class Command(BaseCommand):
    help = '导入食物数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='食物数据文件路径 (支持 .json 和 .csv 格式)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='指定用户名 (必须是已存在的用户)'
        )
        parser.add_argument(
            '--create-user',
            type=str,
            help='创建新用户并导入数据 (用户名)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='导入前清空指定用户的所有食物数据'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际写入数据库'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        user_name = options.get('user')
        create_user = options.get('create_user')
        clear_data = options['clear']
        dry_run = options['dry_run']

        # 验证文件存在
        if not os.path.exists(file_path):
            raise CommandError(f'文件不存在: {file_path}')

        # 处理用户
        if create_user:
            user, created = User.objects.get_or_create(
                username=create_user,
                defaults={
                    'email': f'{create_user}@example.com',
                    'first_name': create_user,
                }
            )
            if created:
                user.set_password('12345678')  # 默认密码
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 创建新用户: {create_user} (密码: 12345678)')
                )
            else:
                self.stdout.write(f'ℹ️  用户已存在: {create_user}')
        elif user_name:
            try:
                user = User.objects.get(username=user_name)
                self.stdout.write(f'ℹ️  使用现有用户: {user_name}')
            except User.DoesNotExist:
                raise CommandError(f'用户不存在: {user_name}')
        else:
            raise CommandError('必须指定 --user 或 --create-user 参数')

        # 清空现有数据
        if clear_data:
            if dry_run:
                count = Foods.objects.filter(user=user).count()
                self.stdout.write(f'🔍 试运行: 将删除 {count} 条现有食物数据')
            else:
                deleted_count = Foods.objects.filter(user=user).delete()[0]
                self.stdout.write(
                    self.style.WARNING(f'🗑️  已删除 {deleted_count} 条现有食物数据')
                )

        # 读取和解析数据
        foods_data = self.load_data(file_path)
        
        # 导入数据
        success_count = 0
        error_count = 0
        
        self.stdout.write(f'📥 开始导入 {len(foods_data)} 条食物数据...')
        
        for i, food_data in enumerate(foods_data, 1):
            try:
                if dry_run:
                    self.stdout.write(f'🔍 试运行 [{i}/{len(foods_data)}]: {food_data.get("name", "未知")}')
                else:
                    self.create_food(user, food_data)
                    self.stdout.write(f'✅ [{i}/{len(foods_data)}]: {food_data.get("name", "未知")}')
                success_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ [{i}/{len(foods_data)}]: {food_data.get("name", "未知")} - {str(e)}')
                )
                error_count += 1

        # 输出结果统计
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🔍 试运行完成! 预计导入 {success_count} 条数据，{error_count} 条错误')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 导入完成! 成功: {success_count}，失败: {error_count}')
            )

    def load_data(self, file_path):
        """加载数据文件"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.json':
            return self.load_json_data(file_path)
        elif file_ext == '.csv':
            return self.load_csv_data(file_path)
        else:
            raise CommandError(f'不支持的文件格式: {file_ext}，仅支持 .json 和 .csv')

    def load_json_data(self, file_path):
        """加载JSON数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 如果是单个对象，转换为列表
            if isinstance(data, dict):
                if 'foods' in data:
                    return data['foods']
                else:
                    return [data]
            elif isinstance(data, list):
                return data
            else:
                raise CommandError('JSON文件格式不正确，应该是对象或数组')
                
        except json.JSONDecodeError as e:
            raise CommandError(f'JSON文件解析错误: {e}')
        except Exception as e:
            raise CommandError(f'读取文件错误: {e}')

    def load_csv_data(self, file_path):
        """加载CSV数据"""
        try:
            foods_data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    foods_data.append(row)
            return foods_data
        except Exception as e:
            raise CommandError(f'读取CSV文件错误: {e}')

    def create_food(self, user, food_data):
        """创建食物记录"""
        # 基本字段映射
        name = food_data.get('name') or food_data.get('食物名称') or food_data.get('食品名称')
        if not name:
            raise ValueError('缺少食物名称')

        # 处理热量数据
        calories = None
        calories_raw = (
            food_data.get('calories') or
            food_data.get('calories_per_100g') or
            food_data.get('热量') or
            food_data.get('热量(千卡/100g)')
        )

        if calories_raw:
            try:
                # 处理各种热量格式：数字、"45/个"、"220/100g"等
                calories_str = str(calories_raw).strip()
                if '/' in calories_str:
                    # 提取数字部分
                    calories_num = calories_str.split('/')[0].strip()
                    calories = int(float(calories_num))
                else:
                    # 直接转换数字
                    calories = int(float(calories_str))
            except (ValueError, TypeError):
                self.stdout.write(f"⚠️  无法解析热量数据: {calories_raw}")
                calories = None

        # 处理描述
        description = food_data.get('description') or food_data.get('描述') or ''

        # 处理餐次适用性 - 从CSV的布尔字段读取
        is_for_breakfast = self.parse_boolean(food_data.get('is_for_breakfast', False))
        is_for_lunch = self.parse_boolean(food_data.get('is_for_lunch', False))
        is_for_afternoon_tea = self.parse_boolean(food_data.get('is_for_afternoon_tea', False))
        is_for_dinner = self.parse_boolean(food_data.get('is_for_dinner', False))
        is_for_supper = self.parse_boolean(food_data.get('is_for_supper', False))

        # 处理标签
        tags = food_data.get('tags') or food_data.get('标签') or ''
        if isinstance(tags, list):
            tags = ','.join(tags)

        # 处理图片URL
        image_url = food_data.get('image_url') or food_data.get('图片链接') or ''

        # 创建食物记录
        food = Foods.objects.create(
            user=user,
            name=name,
            description=description,
            calories=calories,
            is_for_breakfast=is_for_breakfast,
            is_for_lunch=is_for_lunch,
            is_for_afternoon_tea=is_for_afternoon_tea,
            is_for_dinner=is_for_dinner,
            is_for_supper=is_for_supper,
            tags=tags,
            image_url=image_url
        )

        return food

    def parse_boolean(self, value):
        """解析布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', '是')
        return bool(value)
