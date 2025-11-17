from django.core.mail import send_mail
from .models import User
from .generates import generate_code

def send_verification_mail(user_id):
    try:
        user = User.objects.get(id=user_id)
        code = generate_code()
    except User.DoesNotExist:
        raise ValueError("User doesn't exist")
    
    send_mail(
                subject="Verify Your Email",
                message=f"Your Verification code is: {code}",
                from_email="no-reply@fashioncommerce.com",
                recipient_list=[user.email],
                fail_silently=False
            )
    

def send_reset_password_mail(user_id):
    code = generate_code()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValueError("User doesn't exist")
    
    send_mail(
                subject="password reset otp",
                message=f"reset otp code: {code}",
                from_email="no-reply@fashioncommerce.com",
                recipient_list= [user.email],
                fail_silently=False
            )