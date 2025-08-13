from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Profile, Address


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password.')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password fields didn't match.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                 'avatar', 'bio', 'phone', 'birth_date', 'address', 'city', 
                 'postal_code', 'country', 'newsletter_subscription', 
                 'email_notifications', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar', 'bio', 'phone', 'birth_date', 
                 'address', 'city', 'postal_code', 'country', 'newsletter_subscription', 
                 'email_notifications']
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class AddressSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Address
        fields = ['id', 'user', 'user_name', 'address_type', 'first_name', 'last_name',
                 'phone', 'address_line_1', 'address_line_2', 'city', 'state',
                 'postal_code', 'country', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        # Ensure only one default address per user
        user = self.context['request'].user
        if attrs.get('is_default', False):
            # If this is being set as default, unset other defaults
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        return attrs


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_type', 'first_name', 'last_name', 'phone', 
                 'address_line_1', 'address_line_2', 'city', 'state',
                 'postal_code', 'country', 'is_default']
    
    def validate(self, attrs):
        user = self.context['request'].user
        if attrs.get('is_default', False):
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Address.objects.create(user=user, **validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'date_joined', 'profile']
        read_only_fields = ['id', 'username', 'date_joined']