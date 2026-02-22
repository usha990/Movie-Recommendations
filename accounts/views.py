
from django.conf import settings 
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from .models import Profile
import random
from .recommendation import hybrid_recommend

def register_view(request):
    if request.method == "POST":
        username = request.POST['username'].strip()
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = user.profile
        otp = profile.generate_otp()

        # Send OTP email
        send_mail(
            'Your OTP Verification Code',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, "Registration successful! Check your email for OTP.")
        return redirect('email_verification', user_id=user.id)

    return render(request, "accounts/register.html")

# def email_verification_view(request, user_id):
#     profile = Profile.objects.get(user_id=user_id)

#     if request.method == "POST":
#         entered_otp = request.POST.get('otp')

#         if profile.otp == entered_otp:
#             profile.is_verified = True
#             profile.otp = ""
#             profile.save()
#             messages.success(request, "Email verified successfully! You can now login.")
#             return redirect('login')
#         else:
#             messages.error(request, "Invalid OTP. Try again.")

#     return render(request, "accounts/email_verification.html", {"user_id": user.id})
def send_otp_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            profile = Profile.objects.get(user__email=email)
            otp = str(random.randint(100000, 999999))
            profile.otp = otp
            profile.save()
            subject="Your CINEMATCH MOVIE Email Verfication OTP"
            message=f"Hello {profile.user.username},\n\n Your OTP for email Verification is :{otp}\n\n Thank You!"
            from_email="tabharath12345@gmail.com"
            recipient_list=[email]
            send_mail(subject,message,from_email,recipient_list,fail_silently=False)
            # Here, send OTP email
            messages.success(request, f"OTP sent to {email}. Check your email")
            return redirect('email_verification', user_id=profile.user.id)
        except Profile.DoesNotExist:
            messages.error(request, "Email not found. Please register first.")
            return redirect('register')
        
def email_verification_view(request, user_id):
    try:
        profile = Profile.objects.get(user_id=user_id)
        user = profile.user
    except Profile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('register')

    if request.method == "POST":
        input_otp = request.POST.get("otp")
        if input_otp == profile.otp:
            profile.is_verified = True  # mark as verified
            profile.save()
            user=profile.user
            login(request,user)

            # After successful verification, redirect to login
            messages.success(request, "Email verified! Please log in to continue.")
            return redirect("login")  # <-- place it here
 
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "accounts/email_verification.html", {"user_id": user.id})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            if user.profile.is_verified:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Please verify your email before logging in.")
                return redirect('email_verification',user_id=user.id)
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, "accounts/login.html")

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verified! You can now login.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('login')

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')
@login_required
def home_view(request):
    return render(request, 'accounts/home.html', {'username': request.user.username})


from django.shortcuts import render
from .recommendation import hybrid_recommend

from django.shortcuts import render

def recommend_view(request):
    user_id = request.GET.get('user_id', 1)  # Default to user 1 for testing
    try:
        user_id = int(user_id)
    except:
        user_id = 1
    
    recommendations = hybrid_recommend(user_id)
    
    # Debug: Print poster URLs
    print("\n=== RECOMMENDATION DEBUG ===")
    for movie in recommendations:
        print(f"Title: {movie['title']}")
        print(f"Poster URL: {movie.get('poster_url', 'None')}")
        print("-" * 40)
    
    return render(request, 'accounts/recommendation.html', {
        'user_id': user_id,
        'recommendations': recommendations
    })