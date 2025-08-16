from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def login_page(request):
    if request.method== "POST":
        username= request.POST.get('username')
        password= request.POST.get('password')
        user_obj=User.objects.filter(username=username)
        if not user_obj.exists():
            messages.error(request, "Username does not exist.")
            return redirect(request.path_info)
        
        if not user_obj[0].is_active:
            messages.error(request, "Please verify your email first.")
            return redirect(request.path_info)
        
        user_obj= authenticate(username=username, password=password)
        if user_obj:
            login(request,user_obj)
            return redirect("/")
        else:
            messages.error(request, "Invalid username or Password.")
            return redirect(request.path_info)
        
    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # 1️⃣ Check password match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path_info)

        # 2️⃣ Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect(request.path_info)

        # 3️⃣ Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exits.")
            return redirect(request.path_info)

        
        # 4️⃣ Create new user
        user_obj = User.objects.create_user(username=username, email=email, password=password1)
        user_obj.save()

        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")   # redirect to login page

    return render(request, 'accounts/register.html')
