from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages

DEMO_CREDS = [
    ("Admin", "admin", "blue"),
    ("Kafedra mudiri", "kafedra1", "purple"),
    ("O'qituvchi", "teacher1", "green"),
    ("Talaba", "student1", "orange"),
]

def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    error = None
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username','').strip(),
                                     password=request.POST.get('password',''))
        if user:
            login(request, user)
            return redirect(request.GET.get('next', user.get_dashboard_url()))
        error = "Login yoki parol noto'g'ri."
    return render(request, 'auth/login.html', {'error': error, 'demo_creds': DEMO_CREDS})

def logout_view(request):
    logout(request); return redirect('accounts:login')

@login_required
def profile_view(request):
    u = request.user
    if request.method == 'POST':
        u.first_name = request.POST.get('first_name', u.first_name)
        u.last_name  = request.POST.get('last_name',  u.last_name)
        u.phone      = request.POST.get('phone',      u.phone)
        u.bio              = request.POST.get('bio',              u.bio)
        u.telegram_chat_id = request.POST.get('telegram_chat_id', u.telegram_chat_id)
        if u.is_student:
            u.is_accessible = 'is_accessible' in request.POST
        if 'avatar' in request.FILES: u.avatar = request.FILES['avatar']
        np = request.POST.get('new_password','')
        if np: u.set_password(np)
        u.save()
        messages.success(request, "Profil yangilandi.")
        return redirect('accounts:profile')
    from assessment.models import Notification
    notifs = Notification.objects.filter(recipient=u, is_read=False).count()
    return render(request, 'auth/profile.html', {'user': u, 'unread_count': notifs})
