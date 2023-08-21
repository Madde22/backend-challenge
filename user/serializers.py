from abc import ABCMeta, abstractmethod

from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, Group
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user.models import User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation['permissions'] = PermissionSerializer(obj.permissions, many=True).data
        return representation


class UserSerializerForSuperAdmin(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",
                  "username",
                  "email",
                  "first_name",
                  "last_name",
                  "date_joined",
                  "is_active",
                  "is_deleted",
                  "deleted_at",
                  "last_login"
                  )

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        return representation


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id",
                  "username",
                  "email",
                  "first_name",
                  "last_name",
                  "date_joined",
                  "is_active",
                  "is_deleted",
                  "deleted_at",
                  "last_login"
                  )
        read_only_fields = ('date_joined', 'last_login', 'deleted_at')

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        return representation

    def validate_password(self, password):
        """
        Check that the message post is about Django.
        """
        if len(password) < 6:
            raise serializers.ValidationError(_("Password must have at least 6 length!"))
        return password


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",
                  "email",
                  "first_name",
                  "last_name"
                  )

        extra_kwargs = {
            'phone': {'required': True},
            'email': {'required': True},
        }

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        return representation


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    @classmethod
    def get_token(cls, user):
        token = super(CustomTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for register user
    """

    class Meta:
        model = User
        fields = [
                  'username',
                  'password']
        required = ['username', 'phone']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.email = user.username
        user.save()
        return user

    def validate(self, data):
        if 'username' not in data:
            raise serializers.ValidationError(_("Username is required!"))
        elif 'password' not in data:
            raise serializers.ValidationError(_("Password is required!"))

        return data

    def validate_username(self, username):
        """
        Check that the message post is about Django.
        """
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(_("This username is already registered!"))

        return username

    def validate_password(self, password):
        """
        Check that the message post is about Django.
        """
        if len(password) < 6:
            raise serializers.ValidationError(_("Password must have at least 6 length!"))
        return password


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", 'email', 'first_name', 'last_name')


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255)
    re_password = serializers.CharField(max_length=255)
    old_password = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ("id", "password", "re_password", "old_password")

    def validate(self, data):
        if data["password"] != data["re_password"]:
            raise serializers.ValidationError(_(f"Password and re_password are not matched"))
        return data


class PasswordDoneSerializer(serializers.Serializer):
    __metaclass__ = ABCMeta

    uid = serializers.CharField(max_length=255, required=True)
    token = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=20, required=True)

    @abstractmethod
    def validate(self, data):
        # Doing validation
        return data


class MyAuthTokenSerializer(serializers.Serializer):
    __metaclass__ = ABCMeta

    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password", ),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    @abstractmethod
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            # To authenticate call simply returns None for is_active=False users.
            # (Assuming the default ModelBackend authentication backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
