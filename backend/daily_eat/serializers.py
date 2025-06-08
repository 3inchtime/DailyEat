from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Foods, MealLogs, DailyCalorieGoals


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def validate_username(self, value):
        """验证用户名"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        """验证邮箱"""
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被使用")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FoodSerializer(serializers.ModelSerializer):
    """食物序列化器"""
    meal_types = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Foods
        fields = [
            'food_id', 'name', 'description', 'image_url', 'calories',
            'is_for_breakfast', 'is_for_lunch', 'is_for_afternoon_tea',
            'is_for_dinner', 'is_for_supper', 'tags', 'meal_types',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['food_id', 'created_at', 'updated_at', 'meal_types']
    
    def get_meal_types(self, obj):
        """获取适用的餐次类型列表"""
        return obj.get_meal_types()
    
    def validate_calories(self, value):
        """验证卡路里值"""
        if value is not None and value < 0:
            raise serializers.ValidationError("卡路里值不能为负数")
        return value


class MealLogSerializer(serializers.ModelSerializer):
    """用餐记录序列化器"""
    food_detail = FoodSerializer(source='food', read_only=True)
    food_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MealLogs
        fields = [
            'log_id', 'food_id', 'food_detail', 'meal_type_recorded',
            'eaten_at_datetime', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['log_id', 'created_at', 'updated_at', 'food_detail']
    
    def validate_food_id(self, value):
        """验证食物ID是否有效 - 允许使用任何食物"""
        try:
            Foods.objects.get(food_id=value)
        except Foods.DoesNotExist:
            raise serializers.ValidationError("指定的食物不存在")
        return value
    
    def create(self, validated_data):
        """创建用餐记录"""
        food_id = validated_data.pop('food_id')
        user = self.context['request'].user
        # 允许使用任何食物，不限制为当前用户创建的食物
        food = Foods.objects.get(food_id=food_id)
        validated_data['food'] = food
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新用餐记录"""
        if 'food_id' in validated_data:
            food_id = validated_data.pop('food_id')
            # 允许使用任何食物，不限制为当前用户创建的食物
            food = Foods.objects.get(food_id=food_id)
            validated_data['food'] = food
        return super().update(instance, validated_data)


class DailyCalorieGoalSerializer(serializers.ModelSerializer):
    """每日热量目标序列化器"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = DailyCalorieGoals
        fields = ['user_id', 'target_calories', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_target_calories(self, value):
        """验证目标热量值"""
        if value is not None and value < 0:
            raise serializers.ValidationError("目标热量不能为负数")
        if value is not None and value > 10000:
            raise serializers.ValidationError("目标热量不能超过10000千卡")
        return value


class DailyCaloriesStatsSerializer(serializers.Serializer):
    """每日卡路里统计序列化器"""
    date = serializers.DateField()
    total_calories_consumed = serializers.IntegerField()
    target_calories = serializers.IntegerField(allow_null=True)
    remaining_calories = serializers.IntegerField(allow_null=True)
    calorie_deficit_or_surplus = serializers.IntegerField(allow_null=True)
    breakdown_by_meal_type = serializers.DictField()
