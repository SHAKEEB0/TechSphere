from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import ProfileForm, UserRegistrationForm
from .models import Profile, User

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to TechSphere!')
            return redirect('blog:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile saved successfully.')
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = getattr(user, 'profile', None)
    return render(request, 'accounts/profile.html', {'user_profile': profile, 'profile_user': user})
