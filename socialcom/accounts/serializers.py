from rest_framework import serializers
from .models import User, Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'bio', 'profile_image']

        def create(self, validated_data):
            user = User.objects.create_user(
                username = validated_data['email'],
                role = validated_data['role'],
                bio = validated_data.get('bio', ''),
                profile_image = validated_data.get('profile_image', None)
            )

            user.set_password(validated_data['password'])
            user.save()
            return user
        

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        # Django authentication using email
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password."})
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": user.email
        }
        

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError({"detail": "Invalid refresh token"})
        

class ProfileSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = Profile
        fields = ['email', 'full_name', 'bio', 'location', 'profile_image']



class verifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)



class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    