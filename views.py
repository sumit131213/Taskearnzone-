from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import UserProfile, WithdrawalRequest, Task
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='login')
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    now = timezone.now()
    today = timezone.localdate()

    history = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    tasks = Task.objects.filter(is_active=True)

    if profile.last_click_date != today:
        profile.clicks_today = 0
        profile.save()

    if request.method == "POST":
        if profile.clicks_today >= 1:
            messages.error(request, "Today's task is already completed! Please come back tomorrow.")
            return redirect('dashboard')

        profile.balance += 0.50
        profile.clicks_today += 1
        profile.last_click = now
        profile.last_click_date = today
        profile.save()

        messages.success(request, "Congratulations! Rs 0.50 added to your wallet.")
        return redirect('dashboard')

    return render(request, 'earning/dashboard.html', {
        'balance': profile.balance,
        'clicks_left': 1 - profile.clicks_today,
        'history': history,
        'tasks': tasks
    })

@login_required(login_url='login')
def withdraw_view(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        amount_input = request.POST.get('amount')
        upi = request.POST.get('upi')

        try:
            amount = float(amount_input)
        except ValueError:
            messages.error(request, "Please enter a valid amount!")
            return redirect('withdraw')

        if amount > profile.balance:
            messages.error(request, "Insufficient balance in your wallet!")
        elif amount < 40:
            messages.error(request, "Minimum withdrawal amount is Rs.40!")
        else:
            profile.balance -= amount
            profile.save()

            WithdrawalRequest.objects.create(user=request.user, amount=amount, upi_or_paytm=upi)
            messages.success(request, "Request submitted! Monthly processing window is of every day.")
            return redirect('dashboard')

    return render(request, 'earning/withdraw.html', {'balance': profile.balance})

def register_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        p_confirm = request.POST.get('password_confirm')

        if p != p_confirm:
            messages.error(request, "Passwords do not match!")
            return render(request, 'earning/register.html')

        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'earning/register.html')

        if len(p) < 8:
            messages.error(request, "Password must be at least 8 characters long!")
            return render(request, 'earning/register.html')

        user = User.objects.create_user(username=u, password=p)
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect('dashboard')

    return render(request, 'earning/register.html')

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Username or Password!")
    return render(request, 'earning/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def privacy_policy(request):
    return render(request, 'earning/privacy.html')

# --- NAYA REFERRAL SYSTEM (CHECKED) ---
@login_required(login_url='login')
def apply_referral(request):
    if request.method == 'POST':
        code = request.POST.get('ref_code')
        try:
            referrer = User.objects.get(username=code)
            profile = UserProfile.objects.get(user=request.user)

            # Check if fields exist to prevent crash
            if referrer == request.user:
                messages.error(request, "You cannot refer yourself!")
            elif getattr(profile, 'has_used_referral', False):
                messages.error(request, "Already used a code!")
            else:
                referrer_profile = UserProfile.objects.get(user=referrer)
                referrer_profile.balance += 5
                referrer_profile.save()

                profile.referred_by = referrer
                profile.has_used_referral = True
                profile.save()

                messages.success(request, "Success! Rs. 5 added.")
        except:
            messages.error(request, "Invalid Referral Code!")
    return redirect('dashboard')

# ====================================================================
# TASK EARN ZONE - AUTOMATIC AD NETWORK POSTBACK SYSTEM
# ====================================================================
@csrf_exempt
def ad_network_postback(request):
    if request.method == 'GET' or request.method == 'POST':
        user_id = request.GET.get('user_id') or request.POST.get('user_id')
        amount = request.GET.get('amount') or request.POST.get('amount')
        secret_key = request.GET.get('secret') or request.POST.get('secret')

        MY_SECRET_KEY = "TaskEarnZoneSecureKey123"

        if secret_key != MY_SECRET_KEY:
            return HttpResponse("Unauthorized", status=401)

        if user_id and amount:
            try:
                amount_float = float(amount)
                user = User.objects.get(id=user_id)
                profile = UserProfile.objects.get(user=user)
                profile.balance += amount_float
                profile.save()
                return HttpResponse("OK", status=200)
            except:
                return HttpResponse("Error", status=400)
    return HttpResponse("Invalid Method", status=400)

    # ========================================================
# MONLIX AUTOMATIC POSTBACK SYSTEM
# ========================================================
@csrf_exempt
def monlix_postback(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        points = request.GET.get('points')
        status = request.GET.get('status')  # 1 = Success, 2 = Cancel
        secret_key = request.GET.get('secret')

        # Monlix approval ke baad jo secret key milegi, woh yahan aayegi
        MY_MONLIX_SECRET = "TaskEarnZoneMonlixKey123"

        if secret_key != MY_MONLIX_SECRET:
            return HttpResponse("Unauthorized", status=401)

        if user_id and points:
            if status == '1':  # Agar task successfully poora hua hai
                try:
                    user = User.objects.get(id=user_id)
                    profile = UserProfile.objects.get(user=user)

                    # User ke balance mein automatic points plus ho jayenge
                    profile.balance += float(points)
                    profile.save()

                    return HttpResponse("OK", status=200)
                except:
                    return HttpResponse("Error", status=400)

            elif status == '2':  # Reverse/Chargeback ke liye
                return HttpResponse("Chargeback Received", status=200)

    return HttpResponse("Invalid Method", status=400)