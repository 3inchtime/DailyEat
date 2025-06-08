from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Avg
from django.utils.dateparse import parse_date
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import random
from datetime import datetime, date, timedelta

from .models import Foods, MealLogs, DailyCalorieGoals
from .serializers import (
    UserSerializer, UserCreateSerializer, FoodSerializer,
    MealLogSerializer, DailyCaloriesStatsSerializer, DailyCalorieGoalSerializer
)


class UserRegistrationView(CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """创建用户并返回用户信息（不包含密码）"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 返回用户信息，不包含密码
            response_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """获取当前用户信息"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class FoodViewSet(viewsets.ModelViewSet):
    """食物管理视图集"""
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_for_breakfast', 'is_for_lunch', 'is_for_afternoon_tea',
                       'is_for_dinner', 'is_for_supper']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """返回所有食物数据，供所有用户查看"""
        queryset = Foods.objects.all()

        # 检查请求参数中是否有meal_type参数
        # 如果用户明确指定了meal_type，则优先使用该参数
        meal_type = self.request.query_params.get('meal_type', None)
        
        # 如果用户没有指定meal_type，则根据当前时间自动判断餐点类型
        if not meal_type and 'auto_filter_disabled' not in self.request.query_params:
            current_hour = datetime.now().hour
            
            # 根据当前时间段自动判断餐点类型
            if current_hour < 11:  # 早上11点前
                meal_type = '早餐'
            elif 11 <= current_hour < 15:  # 11点到3点
                meal_type = '中餐'
            elif 15 <= current_hour < 18:  # 3点到6点
                meal_type = '下午茶'
            elif 18 <= current_hour < 20:  # 6点到8点
                meal_type = '晚餐'
            else:  # 8点以后
                meal_type = '夜宵'
        
        # 按餐次类型筛选
        if meal_type:
            meal_type_mapping = {
                '早餐': 'is_for_breakfast',
                '中餐': 'is_for_lunch',
                '下午茶': 'is_for_afternoon_tea',
                '晚餐': 'is_for_dinner',
                '夜宵': 'is_for_supper'
            }
            field_name = meal_type_mapping.get(meal_type)
            if field_name:
                queryset = queryset.filter(**{field_name: True})

        # 按标签搜索
        tags_contain = self.request.query_params.get('tags_contain', None)
        if tags_contain:
            queryset = queryset.filter(tags__icontains=tags_contain)

        return queryset

    def perform_create(self, serializer):
        """创建食物时自动关联当前用户"""
        serializer.save(user=self.request.user)

    def get_object(self):
        """获取食物对象，读取操作允许访问所有食物，写入操作只能访问自己的食物"""
        obj = super().get_object()

        # 对于读取操作（GET），允许访问所有食物
        if self.request.method == 'GET':
            return obj

        # 对于写入操作（PUT, PATCH, DELETE），只能访问自己的食物
        if obj.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您没有权限修改此食物")
        return obj

    @action(detail=False, methods=['get'])
    def suggest(self, request):
        """为指定餐次随机推荐一个食物"""
        meal_type = request.query_params.get('meal_type')
        if not meal_type:
            return Response(
                {'error': '必须指定meal_type参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取适合该餐次的食物
        meal_type_mapping = {
            '早餐': 'is_for_breakfast',
            '中餐': 'is_for_lunch',
            '下午茶': 'is_for_afternoon_tea',
            '晚餐': 'is_for_dinner',
            '夜宵': 'is_for_supper'
        }

        field_name = meal_type_mapping.get(meal_type)
        if not field_name:
            return Response(
                {'error': '无效的餐次类型'},
                status=status.HTTP_400_BAD_REQUEST
            )

        foods = Foods.objects.filter(
            **{field_name: True}
        )

        if not foods.exists():
            return Response(
                {'error': f'没有找到适合{meal_type}的食物'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 随机选择一个食物
        suggested_food = random.choice(foods)
        serializer = FoodSerializer(suggested_food)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取食物库统计信息（全局数据）"""
        foods = Foods.objects.all()

        stats_data = {
            'total_foods': foods.count(),
            'breakfast_foods': foods.filter(is_for_breakfast=True).count(),
            'lunch_foods': foods.filter(is_for_lunch=True).count(),
            'afternoon_tea_foods': foods.filter(is_for_afternoon_tea=True).count(),
            'dinner_foods': foods.filter(is_for_dinner=True).count(),
            'supper_foods': foods.filter(is_for_supper=True).count(),
            'foods_with_calories': foods.exclude(calories__isnull=True).count(),
            'average_calories': foods.exclude(calories__isnull=True).aggregate(
                avg_calories=Avg('calories')
            )['avg_calories'] or 0
        }

        return Response(stats_data)


class MealLogViewSet(viewsets.ModelViewSet):
    """用餐记录管理视图集"""
    serializer_class = MealLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['meal_type_recorded']
    ordering_fields = ['eaten_at_datetime', 'created_at']
    ordering = ['-eaten_at_datetime']

    def get_queryset(self):
        """只返回当前用户的用餐记录"""
        queryset = MealLogs.objects.filter(user=self.request.user).select_related('food')

        # 按日期筛选
        date_param = self.request.query_params.get('date', None)
        if date_param:
            try:
                target_date = parse_date(date_param)
                if target_date:
                    queryset = queryset.filter(eaten_at_datetime__date=target_date)
            except ValueError:
                pass

        # 按日期范围筛选
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            try:
                start_date = parse_date(start_date)
                if start_date:
                    queryset = queryset.filter(eaten_at_datetime__date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = parse_date(end_date)
                if end_date:
                    queryset = queryset.filter(eaten_at_datetime__date__lte=end_date)
            except ValueError:
                pass

        return queryset

    def perform_create(self, serializer):
        """创建用餐记录时自动关联当前用户"""
        serializer.save(user=self.request.user)

    def get_object(self):
        """确保用户只能访问自己的用餐记录"""
        obj = super().get_object()
        if obj.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您没有权限访问此用餐记录")
        return obj

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近的用餐记录"""
        limit = int(request.query_params.get('limit', 10))
        recent_logs = MealLogs.objects.filter(
            user=request.user
        ).select_related('food').order_by('-eaten_at_datetime')[:limit]

        serializer = MealLogSerializer(recent_logs, many=True)
        return Response(serializer.data)


class DailyCaloriesStatsAPIView(APIView):
    """每日卡路里统计视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_param = request.query_params.get('date')
        if not date_param:
            return Response(
                {'error': '必须提供date参数 (格式: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date = parse_date(date_param)
            if not target_date:
                raise ValueError("Invalid date format")
        except ValueError:
            return Response(
                {'error': '日期格式无效，请使用 YYYY-MM-DD 格式'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取该用户在指定日期的所有用餐记录
        # 使用时间范围查询避免时区问题
        from django.utils import timezone
        import datetime

        start_of_day = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        meal_logs = MealLogs.objects.filter(
            user=request.user,
            eaten_at_datetime__gte=start_of_day,
            eaten_at_datetime__lte=end_of_day
        ).select_related('food')

        # 计算总卡路里和按餐次分组的卡路里
        total_calories_consumed = 0
        breakdown_by_meal_type = {}

        for log in meal_logs:
            if log.food.calories:
                calories = log.food.calories
                total_calories_consumed += calories

                meal_type = log.meal_type_recorded
                if meal_type in breakdown_by_meal_type:
                    breakdown_by_meal_type[meal_type] += calories
                else:
                    breakdown_by_meal_type[meal_type] = calories

        # 获取用户的热量目标
        try:
            calorie_goal = DailyCalorieGoals.objects.get(user=request.user)
            target_calories = calorie_goal.target_calories
        except DailyCalorieGoals.DoesNotExist:
            target_calories = None

        # 计算剩余热量和热量差额
        remaining_calories = None
        calorie_deficit_or_surplus = None

        if target_calories is not None:
            remaining_calories = target_calories - total_calories_consumed
            calorie_deficit_or_surplus = total_calories_consumed - target_calories

        data = {
            'date': target_date.strftime('%Y-%m-%d'),
            'total_calories_consumed': total_calories_consumed,
            'target_calories': target_calories,
            'remaining_calories': remaining_calories,
            'calorie_deficit_or_surplus': calorie_deficit_or_surplus,
            'breakdown_by_meal_type': breakdown_by_meal_type
        }

        serializer = DailyCaloriesStatsSerializer(data)
        return Response(serializer.data)


class WeeklyStatsAPIView(APIView):
    """周统计视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """获取用户一周的饮食统计"""
        from datetime import timedelta

        # 获取日期参数，默认为今天
        date_param = request.query_params.get('date')
        if date_param:
            try:
                end_date = parse_date(date_param)
                if not end_date:
                    raise ValueError("Invalid date format")
            except ValueError:
                return Response(
                    {'error': '日期格式无效，请使用 YYYY-MM-DD 格式'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            from datetime import date
            end_date = date.today()

        start_date = end_date - timedelta(days=6)  # 7天统计

        # 获取一周内的用餐记录
        # 使用时间范围查询避免时区问题
        from django.utils import timezone
        import datetime

        start_of_period = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
        end_of_period = timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max))

        meal_logs = MealLogs.objects.filter(
            user=request.user,
            eaten_at_datetime__gte=start_of_period,
            eaten_at_datetime__lte=end_of_period
        ).select_related('food')

        # 按日期分组统计
        daily_stats = {}
        for log in meal_logs:
            date_str = log.eaten_at_datetime.date().strftime('%Y-%m-%d')
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    'total_calories': 0,
                    'meal_count': 0,
                    'breakdown_by_meal_type': {}
                }

            if log.food.calories:
                daily_stats[date_str]['total_calories'] += log.food.calories

            daily_stats[date_str]['meal_count'] += 1

            meal_type = log.meal_type_recorded
            if meal_type in daily_stats[date_str]['breakdown_by_meal_type']:
                daily_stats[date_str]['breakdown_by_meal_type'][meal_type] += 1
            else:
                daily_stats[date_str]['breakdown_by_meal_type'][meal_type] = 1

        # 计算周总计
        total_calories = sum(day['total_calories'] for day in daily_stats.values())
        total_meals = sum(day['meal_count'] for day in daily_stats.values())
        avg_daily_calories = total_calories / 7 if total_calories > 0 else 0

        response_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_calories': total_calories,
            'total_meals': total_meals,
            'avg_daily_calories': round(avg_daily_calories, 2),
            'daily_stats': daily_stats
        }

        return Response(response_data)


class DailyCalorieGoalAPIView(APIView):
    """每日热量目标管理视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """获取当前用户的每日热量目标"""
        try:
            goal = DailyCalorieGoals.objects.get(user=request.user)
            serializer = DailyCalorieGoalSerializer(goal)
            return Response(serializer.data)
        except DailyCalorieGoals.DoesNotExist:
            # 返回默认数据，表示用户未设置目标
            data = {
                'user_id': request.user.id,
                'target_calories': None,
                'created_at': None,
                'updated_at': None
            }
            return Response(data)

    def post(self, request):
        """创建新的每日热量目标"""
        # 检查用户是否已有目标
        if DailyCalorieGoals.objects.filter(user=request.user).exists():
            return Response(
                {'error': '用户已有热量目标，请使用PUT方法更新'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = DailyCalorieGoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """更新或创建每日热量目标"""
        goal, created = DailyCalorieGoals.objects.get_or_create(
            user=request.user,
            defaults={'target_calories': None}
        )

        serializer = DailyCalorieGoalSerializer(goal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """删除每日热量目标"""
        try:
            goal = DailyCalorieGoals.objects.get(user=request.user)
            goal.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DailyCalorieGoals.DoesNotExist:
            return Response(
                {'error': '用户没有设置热量目标'},
                status=status.HTTP_404_NOT_FOUND
            )
