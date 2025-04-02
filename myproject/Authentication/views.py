# authentication/views.py
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import SignupForm
from .models import MobileVerification, Profile

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            # ذخیره شماره موبایل در پروفایل کاربر
            mobile = form.cleaned_data.get('mobile')
            user.profile.mobile = mobile
            user.profile.save()
            messages.success(request, "ثبت‌نام با موفقیت انجام شد. لطفا وارد حساب کاربری شوید.")
            return redirect('login')
        else:
            messages.error(request, "خطا در فرم ثبت‌نام. لطفا اطلاعات را به درستی وارد کنید.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # صفحه اصلی یا هر صفحه دلخواه پس از ورود موفق
        else:
            error_message = "نام کاربری یا رمز عبور اشتباه است."
            return render(request, 'login.html', {'error': error_message})
    return render(request, 'login.html')

def forgot_password_view(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        try:
            profile = Profile.objects.get(mobile=mobile)
            user = profile.user
            # تولید کد تایید ۴ رقمی
            code = str(random.randint(1000, 9999))
            MobileVerification.objects.create(user=user, code=code)
            # در اینجا باید از سرویس ارسال پیامک استفاده کنید
            # به عنوان مثال: send_sms(mobile, f"کد تایید شما: {code}")
            messages.success(request, "کد تایید به شماره موبایل ارسال شد.")
            # ذخیره شماره موبایل در سشن برای استفاده در مراحل بعدی
            request.session['mobile'] = mobile
            return redirect('verify_code')
        except Profile.DoesNotExist:
            messages.error(request, "شماره موبایل یافت نشد.")
    return render(request, 'forgot_password.html')

def verify_code_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        mobile = request.session.get('mobile')
        if not mobile:
            messages.error(request, "خطا در بازیابی شماره موبایل. لطفا مجددا تلاش کنید.")
            return redirect('forgot_password')
        try:
            profile = Profile.objects.get(mobile=mobile)
            user = profile.user
            # جستجو برای آخرین کد تایید ارسال شده برای این کاربر
            verification = MobileVerification.objects.filter(user=user, code=code).latest('created')
            # در اینجا می‌توانید زمان انقضای کد را نیز چک کنید
            request.session['reset_user_id'] = user.id
            return redirect('reset_password')
        except (Profile.DoesNotExist, MobileVerification.DoesNotExist):
            messages.error(request, "کد تایید نادرست است.")
    return render(request, 'verify_code.html')

def reset_password_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "خطا در بازیابی اطلاعات کاربر.")
        return redirect('forgot_password')
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        user.set_password(password)
        user.save()
        messages.success(request, "رمز عبور با موفقیت تغییر یافت. لطفا وارد شوید.")
        # پاکسازی سشن
        request.session.pop('reset_user_id', None)
        request.session.pop('mobile', None)
        return redirect('login')
    return render(request, 'reset_password.html')