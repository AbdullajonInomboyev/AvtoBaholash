from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN    = 'admin'
    ROLE_KAFEDRA  = 'kafedra_mudiri'
    ROLE_TEACHER  = 'oqituvchi'
    ROLE_STUDENT  = 'talaba'

    ROLES = [
        (ROLE_ADMIN,   'Admin'),
        (ROLE_KAFEDRA, 'Kafedra Mudiri'),
        (ROLE_TEACHER, "O'qituvchi"),
        (ROLE_STUDENT, 'Talaba'),
    ]

    role         = models.CharField(max_length=20, choices=ROLES, default=ROLE_STUDENT, verbose_name="Rol")
    phone        = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    avatar       = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Rasm")
    bio          = models.TextField(blank=True, verbose_name="Ma'lumot")
    student_id   = models.CharField(max_length=30, blank=True, verbose_name="Talaba ID")
    telegram_chat_id = models.CharField(max_length=50, blank=True, verbose_name='Telegram Chat ID', help_text='Telegram botdan /start bosib olingan ID')
    is_accessible = models.BooleanField(
        default=False,
        verbose_name="Ko'zi ojiz (ovozli rejim)",
        help_text="Agar True bo'lsa, testlar TTS orqali o'qiladi"
    )
    department = models.ForeignKey(
        'core.Department', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='staff',
        verbose_name="Kafedra"
    )
    group = models.ForeignKey(
        'core.Group', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='students',
        verbose_name="Guruh"
    )

    # ---- helpers ----
    @property
    def is_admin(self):    return self.role == self.ROLE_ADMIN
    @property
    def is_kafedra(self):  return self.role == self.ROLE_KAFEDRA
    @property
    def is_teacher(self):  return self.role == self.ROLE_TEACHER
    @property
    def is_student(self):  return self.role == self.ROLE_STUDENT

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}".strip() or self.username

    @property
    def initials(self):
        parts = self.full_name.split()
        return "".join(p[0].upper() for p in parts[:2]) if parts else "?"

    def get_dashboard_url(self):
        from django.urls import reverse
        _map = {
            self.ROLE_ADMIN:   'core:admin_dashboard',
            self.ROLE_KAFEDRA: 'core:kafedra_dashboard',
            self.ROLE_TEACHER: 'core:teacher_dashboard',
            self.ROLE_STUDENT: 'core:student_dashboard',
        }
        return reverse(_map.get(self.role, 'core:dashboard'))

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.full_name} [{self.get_role_display()}]"
