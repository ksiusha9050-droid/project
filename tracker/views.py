from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .checker import PresenceChecker
from .forms import RegisterForm, StartSessionForm, CheckForm
from .models import WorkSession, Check
def get_active_session(user):
    return WorkSession.objects.filter(user=user, is_active=True).first()
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы зарегистрировались!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})
@login_required
def home(request):
    session = get_active_session(request.user)
    if session is None:
        form = StartSessionForm()
        return render(request, 'tracker/home.html', {'form': form})
    checker = PresenceChecker(session)
    check = checker.get_or_create_check()
    context = {
        'session': session,
        'check': check,
        'check_form': CheckForm(),
        'next_check': checker.minutes_to_next_check(),
        'elapsed_seconds': int((timezone.now() - session.start_time).total_seconds()),
    }
    return render(request, 'tracker/home.html', context)
@login_required
def start_session(request):
    if request.method != 'POST':
        return redirect('home')
    if get_active_session(request.user):
        messages.warning(request, 'У вас уже есть начатая сессия.')
        return redirect('home')
    form = StartSessionForm(request.POST)
    if form.is_valid():
        session = form.save(commit=False)
        session.user = request.user
        session.save()
        messages.success(request, 'Работа началась! Не уходите далеко от компьютера :)')
    else:
        messages.error(request, 'Напишите, чем будете заниматься.')
    return redirect('home')
@login_required
def verify(request, check_id):
    check = get_object_or_404(Check, id=check_id, session__user=request.user)
    if request.method == 'POST' and check.answered_at is None:
        form = CheckForm(request.POST)
        if form.is_valid():
            checker = PresenceChecker(check.session)
            if checker.verify(check, form.cleaned_data['code']):
                messages.success(request, 'Проверка пройдена, вы на месте!')
            elif check.is_expired():
                messages.error(request, 'Время на ответ вышло. Проверка не засчитана.')
            else:
                messages.error(request, 'Неверный код. Проверка не засчитана.')
    return redirect('home')
@login_required
def stop_session(request):
    if request.method == 'POST':
        session = get_active_session(request.user)
        if session:
            PresenceChecker(session).close_expired()
            session.finish()
            messages.info(request, f'Сессия завершена. Итог: {session.status()}')
            return redirect('session_detail', session_id=session.id)
    return redirect('home')
@login_required
def history(request):
    sessions = WorkSession.objects.filter(user=request.user)
    return render(request, 'tracker/history.html', {'sessions': sessions})
@login_required
def session_detail(request, session_id):
    session = get_object_or_404(WorkSession, id=session_id, user=request.user)
    checks = session.checks.all()
    return render(request, 'tracker/session_detail.html', {'session': session, 'checks': checks})
@login_required
def stats(request):
    sessions = WorkSession.objects.filter(user=request.user, is_active=False)
    total_minutes = 0
    verified_minutes = 0
    honest_count = 0
    for s in sessions:
        total_minutes += s.duration_minutes()
        verified_minutes += s.verified_minutes()
        if s.status() == 'Честная работа':
            honest_count += 1
    if total_minutes > 0:
        percent = verified_minutes * 100 // total_minutes
    else:
        percent = 0

    context = {
        'sessions_count': sessions.count(),
        'honest_count': honest_count,
        'total_minutes': total_minutes,
        'verified_minutes': verified_minutes,
        'lost_minutes': total_minutes - verified_minutes,
        'percent': percent,
    }
    return render(request, 'tracker/stats.html', context)
