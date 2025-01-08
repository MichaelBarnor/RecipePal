# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Profile
# from .forms import ProfileForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
import logging

logger = logging.getLogger(__name__)

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('home')

    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        logger.error(f"Profile missing for user {request.user.username}")
        profile = None

    return render(request, 'profile.html', {'user': request.user, 'profile': profile})

@login_required
def edit_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        logger.error(f"Profile missing for user {request.user.username}")
        return redirect('profile_page')

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_page')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})
