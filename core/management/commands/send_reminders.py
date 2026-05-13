"""
Deadline yaqinlashganda talabalarga eslatma yuboradi.
Cron yoki Railway scheduler orqali soatiga 1 marta ishga tushiriladi:
    python manage.py send_reminders
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from accounts.models import User
from assessment.models import Assignment, Submission, Notification


class Command(BaseCommand):
    help = "Deadline yaqinlashgan topshiriqlar uchun eslatma yuborish"

    def handle(self, *args, **opts):
        now = timezone.now()
        sent_total = 0

        # 1. 24 soat qoldi
        deadline_24h = now + timedelta(hours=24)
        # 2. 1 soat qoldi
        deadline_1h  = now + timedelta(hours=1)

        for window_label, dl_min, dl_max in [
            ("1 soat", now + timedelta(minutes=50), now + timedelta(minutes=70)),
            ("24 soat", now + timedelta(hours=23), now + timedelta(hours=25)),
        ]:
            assignments = Assignment.objects.filter(
                status='active',
                deadline__gte=dl_min,
                deadline__lte=dl_max,
            ).select_related('subject', 'teacher').prefetch_related('groups')

            for a in assignments:
                # Hali topshirmagan talabalar
                submitted_ids = set(Submission.objects.filter(
                    assignment=a
                ).values_list('student_id', flat=True))

                students = User.objects.filter(
                    role='talaba',
                    group__in=a.groups.all()
                ).exclude(id__in=submitted_ids)

                for s in students:
                    # Allaqachon shu eslatma yuborilganmi?
                    already = Notification.objects.filter(
                        recipient=s,
                        link=f'/dashboard/student/submit/{a.pk}/',
                        title__icontains=window_label,
                    ).exists()

                    if already:
                        continue

                    Notification.objects.create(
                        recipient=s,
                        title=f"⏰ Deadline {window_label} qoldi",
                        message=f"'{a.title}' topshiriqni topshirishga {window_label} qoldi. Kechikmang!",
                        notification_type='deadline_reminder',
                        link=f'/dashboard/student/submit/{a.pk}/',
                    )
                    sent_total += 1

        # 3. Deadline o'tib ketgan, lekin status='active' bo'lganlarni avtomatik 'closed' qilamiz
        expired = Assignment.objects.filter(
            status='active',
            deadline__lt=now
        )
        for a in expired:
            a.status = 'closed'
            a.save(update_fields=['status'])

        self.stdout.write(self.style.SUCCESS(
            f"✅ {sent_total} ta eslatma yuborildi. {expired.count()} ta topshiriq yopildi."
        ))
