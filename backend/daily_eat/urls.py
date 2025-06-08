from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserRegistrationView,
    UserProfileView,
    FoodViewSet,
    MealLogViewSet,
    DailyCaloriesStatsAPIView,
    WeeklyStatsAPIView,
    DailyCalorieGoalAPIView,
)

@api_view(['GET'])
def api_root(request, format=None):
    """
    Daily Eat API Root

    Welcome to the Daily Eat API! This API provides endpoints for managing food data,
    meal logs, user authentication, and statistics.
    """
    return Response({
        'message': 'Welcome to Daily Eat API',
        'version': 'v1',
        'endpoints': {
            'authentication': {
                'register': reverse('user-register', request=request, format=format),
                'login': reverse('token-obtain-pair', request=request, format=format),
                'refresh_token': reverse('token-refresh', request=request, format=format),
                'user_profile': reverse('user-profile', request=request, format=format),
            },
            'foods': {
                'list_create': reverse('foods-list', request=request, format=format),
                'detail': reverse('foods-detail', kwargs={'pk': 1}, request=request, format=format).replace('1', '{id}'),
            },
            'meal_logs': {
                'list_create': reverse('meal-logs-list', request=request, format=format),
                'detail': reverse('meal-logs-detail', kwargs={'pk': 1}, request=request, format=format).replace('1', '{id}'),
            },
            'statistics': {
                'daily_calories': reverse('daily-calories-stats', request=request, format=format),
                'weekly_stats': reverse('weekly-stats', request=request, format=format),
            },
            'goals': {
                'daily_calorie_goal': reverse('daily-calorie-goal', request=request, format=format),
            }
        },
        'documentation': {
            'browsable_api': 'Visit any endpoint URL in your browser for interactive documentation',
            'admin_panel': reverse('admin:index', request=request, format=format),
        }
    })

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'foods', FoodViewSet, basename='foods')
router.register(r'meal-logs', MealLogViewSet, basename='meal-logs')

urlpatterns = [
    # API根视图
    path('', api_root, name='api-root'),

    # 认证相关
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', UserProfileView.as_view(), name='user-profile'),

    # 统计相关
    path('stats/daily-calories/', DailyCaloriesStatsAPIView.as_view(), name='daily-calories-stats'),
    path('stats/weekly/', WeeklyStatsAPIView.as_view(), name='weekly-stats'),

    # 热量目标管理
    path('goals/daily-calorie/', DailyCalorieGoalAPIView.as_view(), name='daily-calorie-goal'),

    # 包含路由器的URL
    path('', include(router.urls)),
]
