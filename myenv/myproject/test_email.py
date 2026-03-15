import os
import django
from django.core.mail import send_mail
from django.conf import settings
import smtplib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_email():
    print("Testing email configuration...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    # Don't print password obviously
    
    try:
        print("Attempting to send email...")
        send_mail(
            'Test Email from HMS',
            'This is a test email to verify SMTP settings.',
            'noreply@hospital.com',
            ['healthcaresanjeevani433@gmail.com'], # Sending to self for test
            fail_silently=False,
        )
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        print("Please check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.")
        print("ensure you are using an App Password if using Gmail with 2FA.")
    except Exception as e:
        print(f"An error occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email()
