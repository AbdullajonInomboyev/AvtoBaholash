from django.db import models
from django.db.models import Count, Avg, Q


class Department(models.Model):
    """Kafedra"""
    name        = models.CharField(max_length=200, unique=True, verbose_name="Kafedra nomi")
    code        = models.CharField(max_length=20,  unique=True, verbose_name="Kod")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Kafedra"
        verbose_name_plural = "Kafedralar"
        ordering            = ['name']

    def __str__(self):
        return self.name

    @property
    def head(self):
        from accounts.models import User
        return User.objects.filter(role=User.ROLE_KAFEDRA, department=self).first()

    @property
    def teachers_count(self):
        from accounts.models import User
        return User.objects.filter(role=User.ROLE_TEACHER, department=self).count()

    @property
    def students_count(self):
        return self.groups.aggregate(
            total=Count('students')
        )['total'] or 0


class Group(models.Model):
    """Talabalar guruhi, masalan: IF-201"""
    name       = models.CharField(max_length=50, verbose_name="Guruh nomi")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        related_name='groups', verbose_name="Kafedra"
    )
    year       = models.PositiveSmallIntegerField(default=1, verbose_name="O'quv yili")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Guruh"
        verbose_name_plural = "Guruhlar"
        ordering            = ['name']
        unique_together     = ['name', 'department']

    def __str__(self):
        return self.name

    @property
    def students_count(self):
        return self.students.count()


class Subject(models.Model):
    """Fan"""
    name        = models.CharField(max_length=200, verbose_name="Fan nomi")
    code        = models.CharField(max_length=20,  verbose_name="Fan kodi")
    department  = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        related_name='subjects', verbose_name="Kafedra"
    )
    credits     = models.PositiveSmallIntegerField(default=3, verbose_name="Kreditlar")
    semester    = models.PositiveSmallIntegerField(default=1, verbose_name="Semestr")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Fan"
        verbose_name_plural = "Fanlar"
        ordering            = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class SubjectTeacher(models.Model):
    """Fan — O'qituvchi — Guruhlar bog'lanishi"""
    subject    = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        related_name='subject_teachers', verbose_name="Fan"
    )
    teacher    = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='teaching_subjects', verbose_name="O'qituvchi"
    )
    groups     = models.ManyToManyField(
        Group, blank=True,
        related_name='subject_teachers', verbose_name="Guruhlar"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Fan biriktirish"
        verbose_name_plural = "Fan biriktirmalar"
        unique_together     = ['subject', 'teacher']

    def __str__(self):
        return f"{self.teacher.full_name} → {self.subject.name}"


class ExamSchedule(models.Model):
    """Imtihon jadvali"""
    subject          = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_schedules', verbose_name="Fan")
    department       = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='exam_schedules', verbose_name="Kafedra")
    groups           = models.ManyToManyField(Group, related_name='exam_schedules', verbose_name="Guruhlar")
    exam_date        = models.DateTimeField(verbose_name="Imtihon sanasi va vaqti")
    room             = models.CharField(max_length=50, blank=True, verbose_name="Xona")
    duration_minutes = models.PositiveIntegerField(default=120, verbose_name="Davomiyligi (daqiqa)")
    notes            = models.TextField(blank=True, verbose_name="Izohlar")
    assignments      = models.ManyToManyField('assessment.Assignment', blank=True, related_name='exams', verbose_name="Topshiriqlar")
    created_by       = models.ForeignKey(
        'accounts.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='created_exams'
    )
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Imtihon jadvali"
        verbose_name_plural = "Imtihon jadvallari"
        ordering            = ['exam_date']

    def __str__(self):
        return f"{self.subject.name} — {self.exam_date.strftime('%d.%m.%Y %H:%M')}"

    @property
    def days_remaining(self):
        from django.utils import timezone
        delta = self.exam_date - timezone.now()
        return delta.days