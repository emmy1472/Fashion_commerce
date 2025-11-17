from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, ProfileSerializer, verifyEmailSerializer, RequestPasswordResetSerializer
from .generates import generate_code
from .models import EmailVerification, User, PasswordResetOTP
from django.core.mail import send_mail




class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code = generate_code()
            EmailVerification.objects.create(user=user, code=code)

            # send email
            send_mail(
                subject="Verify Your Email",
                message=f"Your Verification code is: {code}",
                from_email="no-reply@fashioncommerce.com",
                recipient_list=[user.email]
            )
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
                return Response({"detail": "Verification failed"}, status=status.HTTP_400_BAD_REQUEST)
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
            
            code = generate_code()
            PasswordResetOTP.object.create(user=user, code=code)

            send_mail(
                subject="password reset otp",
                message=f"reset otp code: {code}",
                from_email="no-reply@fashioncommerce.com",
                recipient_list= [user.email]
            )
