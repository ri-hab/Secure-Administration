import random
from django.contrib.auth import login
from django.core.cache import cache
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


def generate_otp(mobile_no):
    otp = random.randint(1000, 9999)
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    
    client.messages.create(
        to=mobile_no,
        from_=settings.TWILIO_FROM_NUMBER,
        body=f'Your One Time Password is {otp}')
    cache.set(mobile_no, otp, 300)
    print(cache.get(mobile_no))
    return True
   

class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)


account_activation_token = AppTokenGenerator()
