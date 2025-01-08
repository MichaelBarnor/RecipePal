from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import uuid
from allauth.socialaccount.models import SocialAccount

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # check if sociallogin already has a user
        if sociallogin.is_existing:
            return

        # check if a user with the same email exists in the database
        email = sociallogin.user.email
        if email:
            try:
                existing_user = sociallogin.user.__class__.objects.get(email=email)
                sociallogin.connect(request, existing_user)
            except sociallogin.user.__class__.DoesNotExist:
                pass
    def populate_user(self, request, sociallogin, data):
        """
        makes sure a unique username is generated for the user during social login/signup
        """
        user = super().populate_user(request, sociallogin, data)

        if not user.username:
            base_username = slugify(data.get("email", "user").split("@")[0])
            unique_username = base_username
            counter = 1

            while user.__class__.objects.filter(username=unique_username).exists():
                unique_username = f"{base_username}{counter}"
                counter += 1

            user.username = unique_username

        return user
    
    def post_social_login(self, request, sociallogin):
        # makes sure socialAccount is created if not already linked
        if not SocialAccount.objects.filter(user=sociallogin.user, provider=sociallogin.account.provider).exists():
            sociallogin.account.user = sociallogin.user
            sociallogin.account.save()
