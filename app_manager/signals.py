# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, pre_delete, post_save
from django.core.mail import send_mail
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist



User = get_user_model()

# this receiver is executed every-time some data is saved in any table
@receiver(pre_save, sender=User)
def activate_user(sender, instance, *args, **kwargs):
    try:
        current_user = instance
        user_pk = current_user._meta.pk.name
        user_pk_value = current_user.__dict__[user_pk]
        query_kwargs = dict()
        query_kwargs[user_pk] = user_pk_value
        prev_instance = sender.objects.get(**query_kwargs) # for dynamic column name
        if not prev_instance.active and current_user.active:
            #send  activation mail
            subject = "Account has been activated"
            first_name = current_user.first_name
            email = current_user.email
            message = "Hi {},\n \nWe are pleased to inform you that your account was activated successfully!\n \nYou can now log in with the email address and password you provided when you signed up.\n \n Thank you for joining us.\n \n3S Jump Server Team".format(first_name)
            from_email = settings.EMAIL_HOST_USER
            to_list = [email, settings.EMAIL_HOST_USER]
            send = send_mail(subject, message, from_email, to_list, fail_silently=False)
            if send:
                print("Mail sent successfully to the activated user!!!")
            else:
                print("We cannot send to mail to the activated user :(")
    except ObjectDoesNotExist as e:
        print("This instance is being created and not updated")

@receiver(pre_delete, sender=User)
def delete_user(sender, instance, *args, **kwargs):
    subject = "Account has been deleted"
    first_name = instance.first_name
    email = instance.email
    message = "Dear {} ,\n \nThank you very much for your registration.\n \n We regret to inform you that your account was deleted!\n \nMay we take this opportunity to thank you for the interest you have shown for our plateform.\n \n3S Jump Server Team".format(first_name)
    from_email = settings.EMAIL_HOST_USER
    to_list = [email, settings.EMAIL_HOST_USER]
    send = send_mail(subject, message, from_email, to_list, fail_silently=False)
    if send:
        print("Mail sent successfully to the deleted user!!!")
    else:
        print("We cannot send to mail to the deleted user :(")



