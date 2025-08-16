from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from account.models import Profile

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if user exists
        user_qs = User.objects.filter(username=username)
        if not user_qs.exists():
            messages.error(request, "Username does not exist.")
            return redirect(request.path_info)

        user_instance = user_qs.first()

# Ensure profile exists
        if not hasattr(user_instance, 'profile'):
          Profile.objects.create(user=user_instance)

        if not user_instance.profile.is_email_verified:
          messages.error(request, "Please verify your email first.")
          return redirect(request.path_info)



        # Authenticate user
        user_obj = authenticate(username=username, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect("/")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect(request.path_info)

    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check password match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path_info)

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect(request.path_info)

        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect(request.path_info)

        # Create new user
        profile = Profile.objects.get(username=username, email=email, password=password1)
        profile.is_email_verified = True
        profile.save()


        messages.success(request, "Account created successfully! Please check your email to verify your account.")
        return redirect("login")

    return render(request, 'accounts/register.html')
