from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please provide both username and password.")

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("accounts:login")


def home_view(request):
    """Home page view."""
    return render(request, "home.html")
