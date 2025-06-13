from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


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


def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validation
        errors = []

        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already exists.")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long.")

        if not email:
            errors.append("Email is required.")
        elif User.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if not password1:
            errors.append("Password is required.")
        elif len(password1) < 8:
            errors.append("Password must be at least 8 characters long.")

        if password1 != password2:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password1)

            # Log the user in automatically
            login(request, user)
            messages.success(
                request, f"Welcome {username}! Your account has been created successfully."
            )
            return redirect("home")

    return render(request, "accounts/signup.html")


@login_required
def profile_view(request):
    """Handle user profile management."""
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            # Handle profile update
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            current_password = request.POST.get("current_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            errors = []

            # Validate username
            if not username:
                errors.append("Username is required.")
            elif (
                username != request.user.username
                and User.objects.filter(username=username).exists()
            ):
                errors.append("Username already exists.")
            elif len(username) < 3:
                errors.append("Username must be at least 3 characters long.")

            # Validate email
            if not email:
                errors.append("Email is required.")
            elif email != request.user.email and User.objects.filter(email=email).exists():
                errors.append("Email already registered.")

            # Validate password change (if provided)
            if new_password:
                if not current_password:
                    errors.append("Current password is required to change password.")
                elif not request.user.check_password(current_password):
                    errors.append("Current password is incorrect.")
                elif len(new_password) < 8:
                    errors.append("New password must be at least 8 characters long.")
                elif new_password != confirm_password:
                    errors.append("New passwords do not match.")

            if errors:
                for error in errors:
                    messages.error(request, error)
            else:
                # Update user information
                request.user.username = username
                request.user.email = email

                # Update password if provided
                if new_password:
                    request.user.set_password(new_password)
                    # Re-authenticate user after password change
                    user = authenticate(request, username=username, password=new_password)
                    if user:
                        login(request, user)

                request.user.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect("accounts:profile")

        elif action == "delete_account":
            # Handle account deletion
            password = request.POST.get("delete_password", "")

            if not password:
                messages.error(request, "Password is required to delete your account.")
            elif not request.user.check_password(password):
                messages.error(request, "Password is incorrect.")
            else:
                # Delete user account
                username = request.user.username
                request.user.delete()
                messages.success(request, f"Account for {username} has been deleted successfully.")
                return redirect("home")

    return render(request, "accounts/profile.html")
