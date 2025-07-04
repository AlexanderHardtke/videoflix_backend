from authemail.models import AbstractBaseCode
from django.conf import settings
from authemail.models import send_multi_format_email

original_send_email = AbstractBaseCode.send_email

def custom_send_email(self, prefix):
    ctxt = {
        'email': self.user.email,
        'first_name': self.user.first_name,
        'last_name': self.user.last_name,
        'code': self.code,
        'frontend_url': settings.FRONTEND_URL,
    }
    send_multi_format_email(prefix, ctxt, target_email=self.user.email)

AbstractBaseCode.send_email = custom_send_email