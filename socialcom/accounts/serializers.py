from rest_framework import serializers
from .models import User, Profile, Role, UserRole
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'bio', 'profile_image']

        def create(self, validated_data):
            role_name = validated_data.pop('role')
            try:
                role = Role.objects.get(name_iexact=role_name)
            except Role.DoesNotExist:
                raise serializers.ValidationError({"role":"Invalid role name."})
            
            user = User.objects.create_user(
                username = validated_data['email'],
                role = role,
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

        roles = UserRole.objects.filter(user=user).values_list("role__name", flat=True)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "roles": list(roles)
            }
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

    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)