from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
class WorkSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    task = models.CharField('Чем занимаюсь', max_length=200)
    start_time = models.DateTimeField('Начало', default=timezone.now)
    end_time = models.DateTimeField('Конец', null=True, blank=True)
    is_active = models.BooleanField('Идёт сейчас', default=True)
    class Meta:
        verbose_name = 'Рабочая сессия'
        verbose_name_plural = 'Рабочие сессии'
        ordering = ['-start_time']
    def __str__(self):
        return f'{self.user.username}: {self.task} ({self.start_time:%d.%m.%Y %H:%M})'
    def finish(self):
        self.end_time = timezone.now()
        self.is_active = False
        self.save()
    def duration_minutes(self):
        end = self.end_time if self.end_time else timezone.now()
        seconds = (end - self.start_time).total_seconds()
        return int(seconds // 60)
    def passed_checks(self):
        return self.checks.filter(passed=True).count()
    def failed_checks(self):
        return self.checks.filter(passed=False, answered_at__isnull=False).count()
    def expected_checks(self):
        return self.duration_minutes() // settings.CHECK_INTERVAL_MINUTES
    def missed_checks(self):
        missed = self.expected_checks() - self.passed_checks()
        if missed < 0:
            missed = 0
        return missed
    def honest_percent(self):
        expected = self.expected_checks()
        if expected == 0:
            return 100
        percent = self.passed_checks() * 100 // expected
        if percent > 100:
            percent = 100
        return percent
    def verified_minutes(self):
        return self.duration_minutes() * self.honest_percent() // 100
    def status(self):
        if self.is_active:
            return 'Идёт'
        percent = self.honest_percent()
        if percent == 100:
            return 'Честная работа'
        elif percent >= 50:
            return 'Есть пропуски'
        else:
            return 'Прогул'
class Check(models.Model):
    session = models.ForeignKey(WorkSession, on_delete=models.CASCADE,
                                related_name='checks', verbose_name='Сессия')
    code = models.CharField('Код', max_length=4)
    created_at = models.DateTimeField('Когда выдан', default=timezone.now)
    answered_at = models.DateTimeField('Когда ответил', null=True, blank=True)
    passed = models.BooleanField('Пройдена', default=False)
    class Meta:
        verbose_name = 'Проверка'
        verbose_name_plural = 'Проверки'
        ordering = ['created_at']
    def __str__(self):
        if self.passed:
            result = 'пройдена'
        elif self.answered_at:
            result = 'провалена'
        else:
            result = 'ждёт ответа'
        return f'Проверка {self.code} — {result}'
    def deadline(self):
        return self.created_at + timedelta(minutes=settings.CODE_LIFETIME_MINUTES)
    def is_expired(self):
        return timezone.now() > self.deadline()
    def seconds_left(self):
        left = (self.deadline() - timezone.now()).total_seconds()
        if left < 0:
            return 0
        return int(left)
