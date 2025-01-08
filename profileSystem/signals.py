from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from allauth.account.signals import user_logged_in
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def create_profile_on_login(sender, request, user, **kwargs):
    if not user.pk:
        return  
    # makes sure the profile exists
    profile, created = Profile.objects.get_or_create(user=user)




@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.get_or_create(user=instance)

    if hasattr(instance, 'profile'):
        instance.profile.save()

