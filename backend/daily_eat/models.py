from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Foods(models.Model):
    """食物表 - 用于存储用户个人食物库中的条目"""

    food_id = models.AutoField(primary_key=True, verbose_name="食物唯一标识")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="所属用户",
        related_name="foods"
    )
    name = models.CharField(max_length=100, verbose_name="食物名称")
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="食物描述/备注/做法"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="食物图片链接"
    )
    calories = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="一份热量（千卡/kcal）",
        help_text="建议非负数"
    )

    # 餐次适用性
    is_for_breakfast = models.BooleanField(default=False, verbose_name="是否适合早餐")
    is_for_lunch = models.BooleanField(default=False, verbose_name="是否适合中餐")
    is_for_afternoon_tea = models.BooleanField(default=False, verbose_name="是否适合下午茶")
    is_for_dinner = models.BooleanField(default=False, verbose_name="是否适合晚餐")
    is_for_supper = models.BooleanField(default=False, verbose_name="是否适合夜宵")

    tags = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="用户自定义标签",
        help_text="多个标签用逗号分隔"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="条目创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="条目最后更新时间")

    class Meta:
        verbose_name = "食物"
        verbose_name_plural = "食物"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_meal_types(self):
        """获取适用的餐次类型列表"""
        meal_types = []
        if self.is_for_breakfast:
            meal_types.append("早餐")
        if self.is_for_lunch:
            meal_types.append("中餐")
        if self.is_for_afternoon_tea:
            meal_types.append("下午茶")
        if self.is_for_dinner:
            meal_types.append("晚餐")
        if self.is_for_supper:
            meal_types.append("夜宵")
        return meal_types


class MealLogs(models.Model):
    """用餐记录表 - 用于记录用户每日的实际用餐情况"""

    MEAL_TYPE_CHOICES = [
        ('早餐', '早餐'),
        ('中餐', '中餐'),
        ('下午茶', '下午茶'),
        ('晚餐', '晚餐'),
        ('夜宵', '夜宵'),
    ]

    log_id = models.AutoField(primary_key=True, verbose_name="用餐记录唯一标识")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="所属用户",
        related_name="meal_logs"
    )
    food = models.ForeignKey(
        Foods,
        on_delete=models.CASCADE,
        verbose_name="记录的具体食物",
        related_name="meal_logs"
    )
    meal_type_recorded = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
        verbose_name="记录的餐次类型"
    )
    eaten_at_datetime = models.DateTimeField(
        default=timezone.now,
        verbose_name="实际用餐日期和时间"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="额外备注"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="记录创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="记录最后更新时间")

    class Meta:
        verbose_name = "用餐记录"
        verbose_name_plural = "用餐记录"
        ordering = ['-eaten_at_datetime']

    def __str__(self):
        return f"{self.user.username} - {self.meal_type_recorded} - {self.food.name} ({self.eaten_at_datetime.date()})"


class DailyCalorieGoals(models.Model):
    """每日热量目标表 - 用于存储用户设定的每日热量摄入目标"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="所属用户",
        related_name="daily_calorie_goal"
    )
    target_calories = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="每日目标摄入热量（千卡/kcal）",
        help_text="用户可能未设置目标"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="目标创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="目标最后更新时间")

    class Meta:
        verbose_name = "每日热量目标"
        verbose_name_plural = "每日热量目标"

    def __str__(self):
        target = self.target_calories if self.target_calories else "未设置"
        return f"{self.user.username} - 目标热量: {target} kcal"
