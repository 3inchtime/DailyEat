from django.contrib import admin
from .models import Foods, MealLogs, DailyCalorieGoals


@admin.register(Foods)
class FoodsAdmin(admin.ModelAdmin):
    """食物管理界面"""
    list_display = ['food_id', 'name', 'user', 'calories', 'created_at']
    list_filter = ['is_for_breakfast', 'is_for_lunch', 'is_for_afternoon_tea',
                   'is_for_dinner', 'is_for_supper', 'created_at']
    search_fields = ['name', 'description', 'tags', 'user__username']
    readonly_fields = ['food_id', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'image_url', 'calories', 'tags')
        }),
        ('餐次适用性', {
            'fields': ('is_for_breakfast', 'is_for_lunch', 'is_for_afternoon_tea',
                      'is_for_dinner', 'is_for_supper')
        }),
        ('系统信息', {
            'fields': ('food_id', 'user', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MealLogs)
class MealLogsAdmin(admin.ModelAdmin):
    """用餐记录管理界面"""
    list_display = ['log_id', 'user', 'food', 'meal_type_recorded', 'eaten_at_datetime']
    list_filter = ['meal_type_recorded', 'eaten_at_datetime', 'created_at']
    search_fields = ['user__username', 'food__name', 'notes']
    readonly_fields = ['log_id', 'created_at', 'updated_at']
    date_hierarchy = 'eaten_at_datetime'
    fieldsets = (
        ('用餐信息', {
            'fields': ('food', 'meal_type_recorded', 'eaten_at_datetime', 'notes')
        }),
        ('系统信息', {
            'fields': ('log_id', 'user', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DailyCalorieGoals)
class DailyCalorieGoalsAdmin(admin.ModelAdmin):
    """每日热量目标管理界面"""
    list_display = ['id', 'user', 'target_calories', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('目标信息', {
            'fields': ('user', 'target_calories')
        }),
        ('系统信息', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
