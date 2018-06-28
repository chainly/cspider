from django.core.signals import got_request_exception
from django.dispatch import receiver

@receiver(got_request_exception)
def my_callback(sender, **kwargs):
    print(locals())
