from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from account.models import Profile


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = authenticate(username=username, password=password)

        if user_obj:
            if not user_obj.profile.is_email_verified:
                messages.error(request, "Email is not verified. Please check your inbox.")
                return HttpResponseRedirect(request.path_info)

            login(request, user_obj)
            return redirect("/")
        else:
            messages.error(request, "Invalid username or password.")
            return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return HttpResponseRedirect(request.path_info)

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists.")
            return HttpResponseRedirect(request.path_info)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create_user(username=username, email=email, password=password1)
        user_obj.save()

        messages.success(request, "Account created successfully! Please check your email to verify your account.")
        return redirect("login")

    return render(request, 'accounts/register.html')


def activate_account(request, token):
    try:
        profile = Profile.objects.get(email_token=token)
        profile.is_email_verified = True
        profile.save()
        messages.success(request, "Your account has been activated successfully!")
        return redirect("login")
    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired activation link.")
        return redirect("register")
