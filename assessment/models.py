from django.db import models
from django.utils import timezone


class Syllabus(models.Model):
    """Fan sillabusi va mavzular ro'yxati"""
    subject     = models.ForeignKey('core.Subject', on_delete=models.CASCADE, related_name='syllabi', verbose_name="Fan")
    teacher     = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='syllabi', verbose_name="O'qituvchi")
    file        = models.FileField(upload_to='syllabi/', blank=True, null=True, verbose_name="Fayl (PDF/DOCX)")
    topics      = models.JSONField(default=list, verbose_name="Mavzular ro'yxati")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Sillabus"
        verbose_name_plural = "Syllabuslar"
        ordering            = ['-uploaded_at']

    def __str__(self):
        return f"{self.subject.name} — Sillabus ({self.uploaded_at.strftime('%d.%m.%Y')})"


class Assignment(models.Model):
    """Topshiriq: test, yozma ish yoki fayl"""
    TYPE_TEST    = 'test'
    TYPE_WRITTEN = 'written'
    TYPE_FILE    = 'file'
    TYPES = [
        (TYPE_TEST,    'Test'),
        (TYPE_WRITTEN, 'Yozma ish'),
        (TYPE_FILE,    'Fayl topshiriq'),
    ]

    STATUS_DRAFT  = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_CLOSED = 'closed'
    STATUSES = [
        (STATUS_DRAFT,  'Qoralama'),
        (STATUS_ACTIVE, 'Faol'),
        (STATUS_CLOSED, 'Yopilgan'),
    ]

    # Asosiy maydonlar
    title           = models.CharField(max_length=200, verbose_name="Sarlavha")
    assignment_type = models.CharField(max_length=20, choices=TYPES, verbose_name="Tur")
    subject         = models.ForeignKey('core.Subject',  on_delete=models.CASCADE, related_name='assignments', verbose_name="Fan")
    teacher         = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='created_assignments', verbose_name="O'qituvchi")
    groups          = models.ManyToManyField('core.Group', related_name='assignments', blank=True, verbose_name="Guruhlar")
    allowed_students = models.ManyToManyField('accounts.User', related_name='allowed_assignments', blank=True,
        limit_choices_to={'role': 'talaba'}, verbose_name="Tanlangan talabalar",
        help_text="Bo'sh qoldirilsa — guruhdagi barcha talabalar")
    description     = models.TextField(blank=True, verbose_name="Tavsif/Savol matni")
    instructions    = models.TextField(blank=True, verbose_name="Ko'rsatmalar")
    deadline        = models.DateTimeField(verbose_name="Topshirish muddati")
    duration_minutes = models.PositiveIntegerField(default=60, verbose_name="Davomiyligi (daqiqa, test uchun)")
    max_score       = models.FloatField(default=100.0, verbose_name="Maksimal ball")
    status          = models.CharField(max_length=20, choices=STATUSES, default=STATUS_DRAFT, verbose_name="Holat")

    # Test sozlamalari
    shuffle_questions      = models.BooleanField(default=True, verbose_name="Savollarni aralashtirish")
    questions_per_student  = models.PositiveIntegerField(default=0,
        verbose_name="Har talabaga necha savol (0=barchasi)")
    show_review_to_student = models.BooleanField(default=False,
        verbose_name="Talabaga savollar tahlilini ko'rsatish",
        help_text="Belgilangan bo'lsa, talaba natija sahifasida o'ziga tushgan savollarni va o'z javoblarini ko'radi (to'g'ri javoblar yashirin)")

    # Fayl topshiriq
    allowed_file_types = models.JSONField(default=list,
        verbose_name="Ruxsat etilgan fayl turlari",
        help_text='Masalan: [".pdf", ".docx"]')
    max_file_size_mb   = models.PositiveIntegerField(default=10, verbose_name="Maks fayl hajmi (MB)")

    # AI tekshiruv natijalari (kafedra mudiriga ko'rinadi, o'qituvchiga emas)
    ai_syllabus_score    = models.FloatField(null=True, blank=True, verbose_name="AI sillabus baho")
    ai_syllabus_feedback = models.TextField(blank=True, verbose_name="AI izohi")
    ai_checked_at        = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Topshiriq"
        verbose_name_plural = "Topshiriqlar"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_assignment_type_display()}]"

    @property
    def is_open(self):
        return self.status == self.STATUS_ACTIVE and timezone.now() <= self.deadline

    @property
    def is_expired(self):
        return timezone.now() > self.deadline

    @property
    def time_remaining(self):
        if self.is_expired:
            return None
        return self.deadline - timezone.now()

    @property
    def submissions_count(self):
        return self.submissions.count()

    @property
    def graded_count(self):
        return self.submissions.filter(status='graded').count()

    def get_ai_score_color(self):
        s = self.ai_syllabus_score
        if s is None: return 'gray'
        if s >= 85:   return 'green'
        if s >= 65:   return 'yellow'
        return 'red'


class Question(models.Model):
    """Test savoli"""
    assignment     = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions', verbose_name="Topshiriq")
    text           = models.TextField(verbose_name="Savol matni")
    text_html      = models.TextField(blank=True, verbose_name="HTML format (formula/rasm uchun)")
    image          = models.ImageField(upload_to='question_images/', blank=True, null=True, verbose_name="Rasm")
    topic          = models.CharField(max_length=100, blank=True, verbose_name="Mavzu")
    difficulty     = models.CharField(max_length=10, default='medium', choices=[
        ('easy','Oson'),('medium',"O'rta"),('hard','Qiyin')
    ], verbose_name="Qiyinlik darajasi")
    points         = models.PositiveIntegerField(default=1, verbose_name="Ball")
    image_a        = models.ImageField(upload_to='option_images/', blank=True, null=True, verbose_name="A variant rasmi")
    image_b        = models.ImageField(upload_to='option_images/', blank=True, null=True, verbose_name="B variant rasmi")
    image_c        = models.ImageField(upload_to='option_images/', blank=True, null=True, verbose_name="C variant rasmi")
    image_d        = models.ImageField(upload_to='option_images/', blank=True, null=True, verbose_name="D variant rasmi")
    topic          = models.CharField(max_length=200, blank=True, verbose_name="Mavzu")
    # Javob variantlari
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')],
                                      verbose_name="To'g'ri javob")
    option_a       = models.TextField(verbose_name="A variant")
    option_b       = models.TextField(verbose_name="B variant")
    option_c       = models.TextField(verbose_name="C variant")
    option_d       = models.TextField(blank=True, verbose_name="D variant (ixtiyoriy)")
    # Inklyuziv
    is_accessible  = models.BooleanField(default=True,
        verbose_name="TTS uchun mos",
        help_text="Ko'zi ojiz talabalar uchun ovozli o'qilishi mumkinmi")
    order          = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name        = "Savol"
        verbose_name_plural = "Savollar"
        ordering            = ['order', 'pk']

    def __str__(self):
        return f"#{self.order} {self.text[:60]}"

    def get_options(self):
        """(harf, matn, rasm_url)"""
        opts = []
        for letter in ['A', 'B', 'C', 'D']:
            text  = getattr(self, f'option_{letter.lower()}', '')
            image = getattr(self, f'image_{letter.lower()}', None)
            if text or (image and image.name):
                opts.append((letter, text, image.url if image and image.name else None))
        return opts


class Submission(models.Model):
    """Talabaning javobi"""
    STATUS_SUBMITTED = 'submitted'
    STATUS_GRADED    = 'graded'
    STATUS_DISPUTED  = 'disputed'
    STATUSES = [
        (STATUS_SUBMITTED, 'Topshirildi'),
        (STATUS_GRADED,    'Baholandi'),
        (STATUS_DISPUTED,  'Shikoyat'),
    ]

    assignment   = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student      = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, choices=STATUSES, default=STATUS_SUBMITTED)

    # Test javobi: {question_id: "A"/"B"/"C"/"D"}
    test_answers = models.JSONField(default=dict)

    # Yozma ish
    text_answer  = models.TextField(blank=True)

    # Fayl
    uploaded_file = models.FileField(upload_to='submissions/', blank=True, null=True)

    # Anti-cheat
    tab_switches       = models.PositiveIntegerField(default=0)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    ip_address         = models.GenericIPAddressField(null=True, blank=True)
    suspicious_events  = models.JSONField(default=list)

    # AI baholash
    ai_score      = models.FloatField(null=True, blank=True)
    ai_feedback   = models.TextField(blank=True)
    ai_graded_at  = models.DateTimeField(null=True, blank=True)
    ai_strengths  = models.JSONField(default=list, blank=True, verbose_name="AI: kuchli tomonlar")
    ai_improvements=models.JSONField(default=list, blank=True, verbose_name="AI: yaxshilash kerak")
    ai_syllabus_fb = models.TextField(blank=True, verbose_name="AI sillabus izohi")

    # O'qituvchi tasdiqlagan baho
    final_score  = models.FloatField(null=True, blank=True)
    teacher_note = models.TextField(blank=True)
    graded_by    = models.ForeignKey(
        'accounts.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    # Appeal — bahoga e'tiroz
    APPEAL_CHOICES = [
        ('none', "Yo'q"),
        ('pending', "Ko'rib chiqilmoqda"),
        ('reviewing', "Qayta tekshirilmoqda"),
        ('accepted', "Qabul qilindi"),
        ('rejected', "Rad etildi"),
    ]
    appeal_status   = models.CharField(max_length=20, default='none', choices=APPEAL_CHOICES, verbose_name="E'tiroz holati")
    appeal_reason   = models.TextField(blank=True, verbose_name="E'tiroz sababi")
    appeal_response = models.TextField(blank=True, verbose_name="O'qituvchi javobi")
    appealed_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = "Javob"
        verbose_name_plural = "Javoblar"
        unique_together     = ['assignment', 'student']
        ordering            = ['-submitted_at']

    def __str__(self):
        return f"{self.student.full_name} → {self.assignment.title}"

    @property
    def display_score(self):
        s = self.final_score if self.final_score is not None else self.ai_score
        return f"{s:.1f}" if s is not None else "—"

    @property
    def grade_letter(self):
        """5 ballik tizim: 5=86-100, 4=71-85, 3=56-70, 2=41-55, 1=0-40"""
        s = self.final_score if self.final_score is not None else self.ai_score
        if s is None: return "—"
        if s >= 86:   return "5"
        if s >= 71:   return "4"
        if s >= 56:   return "3"
        if s >= 41:   return "2"
        return "1"

    @property
    def grade_color(self):
        """5: yashil, 4: ko'k, 3: sariq, 2: to'q sariq, 1: qizil"""
        s = self.final_score if self.final_score is not None else self.ai_score
        if s is None:  return 'gray'
        if s >= 86:    return 'green'   # 5
        if s >= 71:    return 'blue'    # 4
        if s >= 56:    return 'yellow'  # 3
        if s >= 41:    return 'orange'  # 2
        return 'red'                    # 1

    @property
    def is_suspicious(self):
        return self.tab_switches > 3 or bool(self.suspicious_events)


class SubmissionImage(models.Model):
    """Yozma ish uchun yuklangan rasmlar"""
    submission  = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='images')
    image       = models.ImageField(upload_to='submission_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    """Talabaning shikoyati"""
    STATUS_OPEN      = 'open'
    STATUS_ANSWERED  = 'answered'
    STATUS_ESCALATED = 'escalated'
    STATUS_CLOSED    = 'closed'
    STATUSES = [
        (STATUS_OPEN,      'Ochiq'),
        (STATUS_ANSWERED,  'Javob berildi'),
        (STATUS_ESCALATED, 'Kafedra mudiriga yuborildi'),
        (STATUS_CLOSED,    'Yopildi'),
    ]

    submission      = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='feedbacks')
    student         = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='my_feedbacks')
    message         = models.TextField(verbose_name="Shikoyat matni")
    status          = models.CharField(max_length=20, choices=STATUSES, default=STATUS_OPEN)
    created_at      = models.DateTimeField(auto_now_add=True)
    teacher_response = models.TextField(blank=True)
    responded_at    = models.DateTimeField(null=True, blank=True)
    escalated_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = "Feedback"
        verbose_name_plural = "Feedbacklar"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name} — {self.get_status_display()}"


class Notification(models.Model):
    """Tizim bildirishnomalari"""
    TYPE_INFO    = 'info'
    TYPE_WARNING = 'warning'
    TYPE_SUCCESS = 'success'
    TYPE_ERROR   = 'error'
    TYPES = [
        (TYPE_INFO,    "Ma'lumot"),
        (TYPE_WARNING, 'Ogohlantirish'),
        (TYPE_SUCCESS, 'Muvaffaqiyat'),
        (TYPE_ERROR,   'Xato'),
    ]

    recipient         = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title             = models.CharField(max_length=200)
    message           = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES, default=TYPE_INFO)
    is_read           = models.BooleanField(default=False)
    link              = models.CharField(max_length=300, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"
        ordering            = ['-created_at']

    def __str__(self):
        return f"→ {self.recipient.username}: {self.title}"


class AIAnalysisLog(models.Model):
    """AI tekshiruv jurnali (kafedra mudiri uchun)"""
    TYPE_SYLLABUS    = 'syllabus_check'
    TYPE_GRADING     = 'auto_grading'
    TYPE_ACCESSIBLE  = 'accessibility'
    TYPES = [
        (TYPE_SYLLABUS,   'Sillabus tekshiruvi'),
        (TYPE_GRADING,    'Avtomatik baholash'),
        (TYPE_ACCESSIBLE, 'Inklyuziv tekshiruv'),
    ]

    assignment    = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='ai_logs')
    analysis_type = models.CharField(max_length=30, choices=TYPES)
    result        = models.JSONField(default=dict)
    score         = models.FloatField(null=True, blank=True)
    feedback      = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "AI jurnal"
        verbose_name_plural = "AI jurnal yozuvlari"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.assignment.title} — {self.get_analysis_type_display()}"


# ─────────────────────────────────────────────────
# SAVOL BANKI (Question Bank)
# ─────────────────────────────────────────────────

class QuestionBank(models.Model):
    """O'qituvchining qayta ishlatiluvchi savollar to'plami"""
    teacher     = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='question_banks')
    subject     = models.ForeignKey('core.Subject',  on_delete=models.CASCADE, related_name='question_banks')
    title       = models.CharField(max_length=200, verbose_name="Bank nomi")
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Savol banki"
        verbose_name_plural = "Savol banklari"
        ordering            = ['-updated_at']
        unique_together     = ['teacher', 'subject', 'title']

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

    @property
    def questions_count(self):
        return self.bank_questions.count()


class BankQuestion(models.Model):
    """Savollar bankidagi savol"""
    bank           = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='bank_questions')
    text           = models.TextField(verbose_name="Savol matni")
    image          = models.ImageField(upload_to='bank_questions/', blank=True, null=True)
    topic          = models.CharField(max_length=200, blank=True, verbose_name="Mavzu")
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    option_a       = models.TextField()
    option_b       = models.TextField()
    option_c       = models.TextField()
    option_d       = models.TextField(blank=True)
    difficulty     = models.CharField(max_length=10, choices=[
        ('easy','Oson'), ('medium','O\'rtacha'), ('hard','Qiyin')
    ], default='medium')
    is_duplicate   = models.BooleanField(default=False, verbose_name="Takroriy savol (AI)")
    duplicate_note = models.CharField(max_length=200, blank=True)
    use_count      = models.PositiveIntegerField(default=0, verbose_name="Ishlatilgan marta")
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Bank savoli"
        verbose_name_plural = "Bank savollari"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.bank.title} — {self.text[:50]}"

    def get_options(self):
        """BankQuestion uchun — (harf, matn, None)"""
        opts = []
        for letter in ['A', 'B', 'C', 'D']:
            text = getattr(self, f'option_{letter.lower()}', '')
            if text:
                opts.append((letter, text, None))
        return opts


class TopicQuota(models.Model):
    """Topshiriqdagi har mavzu uchun nechta savol kelishini belgilash"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='topic_quotas')
    topic      = models.CharField(max_length=200, verbose_name="Mavzu")
    count      = models.PositiveIntegerField(default=1, verbose_name="Savol soni")

    class Meta:
        verbose_name        = "Mavzu kvotasi"
        verbose_name_plural = "Mavzu kvotalari"
        unique_together     = ['assignment', 'topic']

    def __str__(self):
        return f"{self.assignment.title} — {self.topic}: {self.count} ta"