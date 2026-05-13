"""
python manage.py clear_demo

DB dagi BARCHA ma'lumotlarni o'chiradi (admin dan tashqari).
DIQQAT: Bu buyruq faqat ehtiyotkorlik bilan ishlatilsin!
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User


class Command(BaseCommand):
    help = "Barcha demo ma'lumotlarni o'chiradi (admin dan tashqari)"

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true', help="Tasdiqsiz o'chiradi")

    def handle(self, *args, **opts):
        if not opts['yes']:
            self.stdout.write(self.style.WARNING("⚠️  Bu buyruq DB dagi BARCHA ma'lumotlarni o'chiradi!"))
            self.stdout.write("Tasdiqlash uchun: python manage.py clear_demo --yes")
            return

        from core.models       import Department, Group, Subject, SubjectTeacher, ExamSchedule
        from assessment.models import (
            Syllabus, Assignment, Question, Submission, Feedback, Notification,
            AIAnalysisLog, QuestionBank, BankQuestion, TopicQuota, SubmissionImage
        )

        with transaction.atomic():
            counts = {}

            # Submissionga bog'liq
            counts['Feedback']           = Feedback.objects.all().delete()[0]
            counts['SubmissionImage']    = SubmissionImage.objects.all().delete()[0]
            counts['Submission']         = Submission.objects.all().delete()[0]

            # Assignment
            counts['AIAnalysisLog']      = AIAnalysisLog.objects.all().delete()[0]
            counts['TopicQuota']         = TopicQuota.objects.all().delete()[0]
            counts['Question']           = Question.objects.all().delete()[0]
            counts['Assignment']         = Assignment.objects.all().delete()[0]

            # Question bank
            counts['BankQuestion']       = BankQuestion.objects.all().delete()[0]
            counts['QuestionBank']       = QuestionBank.objects.all().delete()[0]

            # Boshqa
            counts['Notification']       = Notification.objects.all().delete()[0]
            counts['Syllabus']           = Syllabus.objects.all().delete()[0]
            counts['ExamSchedule']       = ExamSchedule.objects.all().delete()[0]
            counts['SubjectTeacher']     = SubjectTeacher.objects.all().delete()[0]

            # Foydalanuvchilar (admin dan tashqari)
            counts['User']               = User.objects.exclude(is_superuser=True).delete()[0]

            # Kafedra/guruh/fan
            counts['Subject']            = Subject.objects.all().delete()[0]
            counts['Group']              = Group.objects.all().delete()[0]
            counts['Department']         = Department.objects.all().delete()[0]

        self.stdout.write(self.style.SUCCESS("✅ Tozalandi:"))
        for model, n in counts.items():
            if n > 0:
                self.stdout.write(f"   {model}: {n} ta")

        admin_count = User.objects.filter(is_superuser=True).count()
        self.stdout.write(self.style.SUCCESS(f"\n👤 Adminlar saqlanib qoldi: {admin_count} ta"))