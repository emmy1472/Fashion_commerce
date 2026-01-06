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
        # Validate role against the choices on the User model
        role_name = validated_data.pop('role')
        allowed = [choice[0] for choice in User.ROLE_CHOICES]
        if role_name not in allowed:
            raise serializers.ValidationError({"role": "Invalid role name."})

        password = validated_data.pop('password')
        username = validated_data.get('username') or validated_data.get('email')

        user = User.objects.create_user(
            username=username,
            email=validated_data.get('email')
        )
        user.role = role_name
        user.bio = validated_data.get('bio', '')
        if validated_data.get('profile_image'):
            user.profile_image = validated_data.get('profile_image')
        user.set_password(password)
        user.save()
        return user
        

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        # Django authentication using email
        # since USERNAME_FIELD = 'email' on our User model, pass it as username
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password."})
        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Prefer role stored on User; also include any role objects
        roles = [user.role] if getattr(user, 'role', None) else []
        roles += list(UserRole.objects.filter(user=user).values_list("role__name", flat=True))
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



class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)



class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        # Run Django password validators
        validate_password(value)
        return value


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (public-facing fields)."""
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "bio", "profile_image"]