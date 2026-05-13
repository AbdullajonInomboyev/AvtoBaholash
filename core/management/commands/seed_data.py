"""
python manage.py seed_data

AvtoBaholash uchun MINIMAL ma'lumot yaratadi:
- Faqat 1 ta superuser admin
- Boshqa hech qanday demo ma'lumot yo'q
- Foydalanuvchi qolganini o'zi yaratadi
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Faqat admin yaratadi (boshqa demo ma'lumotsiz)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--password',
            default='admin123',
            help='Admin password (default: admin123)'
        )
        parser.add_argument(
            '--email',
            default='admin@avtobaho.uz',
            help='Admin email'
        )

    def handle(self, *args, **opts):
        username = opts['username']
        password = opts['password']
        email    = opts['email']

        if User.objects.filter(username=username).exists():
            u = User.objects.get(username=username)
            u.set_password(password)
            u.is_superuser = True
            u.is_staff     = True
            u.role         = 'admin'
            u.save()
            self.stdout.write(self.style.WARNING(
                f"⚠️  Admin '{username}' allaqachon mavjud edi — parol yangilandi."
            ))
        else:
            User.objects.create_superuser(
                username   = username,
                password   = password,
                email      = email,
                first_name = 'Tizim',
                last_name  = 'Administratori',
                role       = 'admin',
            )
            self.stdout.write(self.style.SUCCESS(
                f"✅ Admin yaratildi"
            ))

        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        self.stdout.write(self.style.SUCCESS(f"   Login:  {username}"))
        self.stdout.write(self.style.SUCCESS(f"   Parol:  {password}"))
        self.stdout.write(self.style.SUCCESS("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        self.stdout.write("")
        self.stdout.write("Endi admin panelda kerakli ma'lumotlarni qo'shing:")
        self.stdout.write("  1. Kafedra qo'shing")
        self.stdout.write("  2. Guruhlar qo'shing")
        self.stdout.write("  3. Fanlarni qo'shing")
        self.stdout.write("  4. O'qituvchi va talabalarni qo'shing")