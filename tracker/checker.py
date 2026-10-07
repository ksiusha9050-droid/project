import random
from django.conf import settings
from django.utils import timezone
from .models import Check
class PresenceChecker:
    def __init__(self, session):
        self.session = session
        self.interval = settings.CHECK_INTERVAL_MINUTES
    def last_check(self):
        return self.session.checks.order_by('-created_at').first()
    def close_expired(self):
        waiting = self.session.checks.filter(answered_at__isnull=True)
        for check in waiting:
            if check.is_expired():
                check.answered_at = check.deadline()
                check.passed = False
                check.save()
    def current_check(self):
        self.close_expired()
        return self.session.checks.filter(answered_at__isnull=True).first()
    def need_new_check(self):
        last = self.last_check()
        if last is None:
            since = self.session.start_time
        else:
            since = last.created_at
        minutes_passed = (timezone.now() - since).total_seconds() / 60
        return minutes_passed >= self.interval
    def create_check(self):
        code = str(random.randint(1000, 9999))
        return Check.objects.create(session=self.session, code=code)
    def get_or_create_check(self):
        check = self.current_check()
        if check is None and self.need_new_check():
            check = self.create_check()
        return check
    def verify(self, check, entered_code):
        check.answered_at = timezone.now()
        if check.is_expired():
            check.passed = False
        elif entered_code.strip() == check.code:
            check.passed = True
        else:
            check.passed = False
        check.save()
        return check.passed
    def minutes_to_next_check(self):
        last = self.last_check()
        since = last.created_at if last else self.session.start_time
        passed = (timezone.now() - since).total_seconds() / 60
        left = self.interval - passed
        if left < 0:
            left = 0
        return int(left) + 1
