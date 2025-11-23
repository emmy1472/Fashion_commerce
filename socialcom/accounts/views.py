from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, ProfileSerializer, verifyEmailSerializer, RequestPasswordResetSerializer, ResetPasswordSerializer
from .generates import generate_code
from .models import EmailVerification, User, PasswordResetOTP
from django.core.mail import send_mail

from .send_mails import send_verification_mail, send_reset_password_mail, code


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            EmailVerification.objects.create(user=user, code=code)
            send_verification_mail(user.id)
            return Response(
                {"message": "Account created successfully", "user": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def post(self, request):
        serializer = verifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                verification = EmailVerification.objects.filter(user=user, code=code).first()
                if not verification:
                    return Response({"detail": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
                
                user.is_verified = True
                user.save()

                verification.delete()
                return Response({"detail": "Verification sucessful"}, status=status.HTTP_200_OK)
            except Exception:
                return Response({"detail" : "Verification failed"}, status=status.HTTP_400_BAD_REQUEST)



class RequestPasswordResetView(APIView):
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            PasswordResetOTP.objects.create(user=user, code=code)
            send_reset_password_mail(user.id)
            return Response(
                {"message": "The code has been sent your email", "email": email},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            

            


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            reset_obj = PasswordResetOTP.objects.filter(user=user, code=code).first()

            if not reset_obj:
                return Response({"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
            
            if reset_obj.is_expired():
                return Response({"detail": "Code expired"}, status=status.HTTP_400_BAD_REQUEST)
            
            # change password
            user.set_password(new_password)
            user.save()

            reset_obj.delete()

            return Response({"detail": "Password reset succesfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
