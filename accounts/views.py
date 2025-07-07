from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm, CustomUserCreationForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('properties:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('properties:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('properties:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to BookMyProperty, {user.first_name}!')
            return redirect('properties:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('properties:home')

@login_required
def profile_view(request):
    bookings = None
    if request.user.userprofile.user_type == 'tenant':
        bookings = request.user.bookings.all().order_by('-created_at')
    show_form = request.GET.get('edit') == '1' or request.method == 'POST'
    if show_form:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('auth:profile')
        else:
            form = UserProfileForm(instance=request.user.userprofile)
    else:
        form = None
    context = {
        'form': form,
        'bookings': bookings,
        'user': request.user,
        'show_reset_pwd': True,
        'show_form': show_form,
    }
    return render(request, 'accounts/profile.html', context)
