import random
from django.core.mail import send_mail
from django.utils import timezone
from .models import OTP

def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(user, otp_code):
    """Send OTP to user's email"""
    subject = 'Your OTP for Hospital Management System'
    message = f'''
Hello {user.username},

Your OTP for login is: {otp_code}

This OTP is valid for 5 minutes only.

If you didn't request this, please ignore this email.

Best regards,
Hospital Management Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            'noreply@hospital.com',
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

from django.conf import settings
try:
    from twilio.rest import Client
except ImportError:
    Client = None

def send_otp_sms(user, otp_code):
    """Send OTP to user's phone via Twilio"""
    if not user.phone:
        return False
        
    message_body = f"Your OTP for Hospital Management System is: {otp_code}. Valid for 5 minutes."
    
    # Check if Twilio is configured
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
    
    if account_sid and auth_token and from_number and Client:
        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=user.phone
            )
            print(f"SMS sent successfully via Twilio: {message.sid}")
            return True
        except Exception as e:
            print(f"Error sending SMS via Twilio: {e}")
            return False
            
    else:
        # Fallback to Mock if keys are missing
        print("="*50)
        print("TWILIO CREDENTIALS MISSING - FALLING BACK TO MOCK")
        print(f"Sending SMS to {user.phone}:")
        print(message_body)
        print("="*50)
        return True

def create_otp(user):
    """Create and save OTP for user"""
    # Invalidate any existing OTPs
    OTP.objects.filter(user=user, is_verified=False).update(is_verified=True)
    
    # Generate new OTP
    otp_code = generate_otp()
    otp = OTP.objects.create(user=user, otp_code=otp_code)
    
    # Send OTP via Email and SMS
    send_otp_email(user, otp_code)
    # send_otp_sms(user, otp_code) # SMS disabled per user request
    
    return otp

def verify_otp(user, otp_code):
    """Verify OTP for user"""
    try:
        otp = OTP.objects.filter(
            user=user,
            is_verified=False
        ).latest('created_at')
        
        # Check if expired
        if otp.is_expired():
            return False, "OTP has expired. Please request a new one."
        
        # Check attempts
        if otp.attempts >= 3:
            return False, "Maximum attempts reached. Please request a new OTP."
        
        # Verify code
        if otp.otp_code == otp_code:
            otp.is_verified = True
            otp.save()
            return True, "OTP verified successfully!"
        else:
            otp.attempts += 1
            otp.save()
            remaining = 3 - otp.attempts
            return False, f"Invalid OTP. {remaining} attempts remaining."
            
    except OTP.DoesNotExist:
        return False, "No active OTP found. Please request a new one."

def cleanup_expired_otps():
    """Delete expired OTPs"""
    OTP.objects.filter(expires_at__lt=timezone.now()).delete()
