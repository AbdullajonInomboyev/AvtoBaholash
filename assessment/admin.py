from django.contrib import admin
from django.utils.html import format_html
from .models import (Syllabus, Assignment, Question, Submission,
                     SubmissionImage, Feedback, Notification, AIAnalysisLog)


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display  = ['subject', 'teacher', 'topics_count', 'uploaded_at']
    list_filter   = ['subject__department']
    search_fields = ['subject__name', 'teacher__username']

    def topics_count(self, obj): return len(obj.topics)
    topics_count.short_description = "Mavzular"


class QuestionInline(admin.TabularInline):
    model  = Question
    extra  = 0
    fields = ['order', 'text', 'correct_answer', 'option_a', 'option_b', 'option_c', 'is_accessible']
    ordering = ['order']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display  = ['title', 'assignment_type', 'subject', 'teacher', 'status',
                     'deadline', 'submissions_count', 'ai_score_badge']
    list_filter   = ['assignment_type', 'status', 'subject__department']
    search_fields = ['title', 'teacher__username', 'subject__name']
    filter_horizontal = ['groups']
    inlines       = [QuestionInline]
    readonly_fields = ['ai_syllabus_score', 'ai_syllabus_feedback', 'ai_checked_at',
                       'created_at', 'updated_at']

    def submissions_count(self, obj): return obj.submissions_count
    submissions_count.short_description = "Javoblar"

    def ai_score_badge(self, obj):
        s = obj.ai_syllabus_score
        if s is None: return "—"
        color = '#22c55e' if s>=85 else ('#f59e0b' if s>=65 else '#ef4444')
        return format_html('<span style="color:{};font-weight:bold">{:.0f}%</span>', color, s)
    ai_score_badge.short_description = "AI baho"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ['order', 'assignment', 'text_short', 'correct_answer', 'topic', 'is_accessible']
    list_filter   = ['assignment__subject', 'correct_answer', 'is_accessible']
    search_fields = ['text', 'topic']

    def text_short(self, obj): return obj.text[:60]
    text_short.short_description = "Savol"


class SubmissionImageInline(admin.TabularInline):
    model  = SubmissionImage
    extra  = 0
    fields = ['image', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display   = ['student', 'assignment', 'status', 'display_score',
                      'grade_letter', 'tab_switches', 'submitted_at']
    list_filter    = ['status', 'assignment__subject__department']
    search_fields  = ['student__username', 'student__last_name', 'assignment__title']
    readonly_fields = ['test_answers', 'ai_score', 'ai_feedback', 'ai_graded_at',
                       'submitted_at', 'ip_address', 'tab_switches', 'suspicious_events']
    inlines        = [SubmissionImageInline]

    def display_score(self, obj): return obj.display_score
    display_score.short_description = "Ball"

    def grade_letter(self, obj): return obj.grade_letter
    grade_letter.short_description = "Baho"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display  = ['student', 'submission', 'status', 'created_at', 'responded_at']
    list_filter   = ['status']
    search_fields = ['student__username', 'message']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter   = ['notification_type', 'is_read']
    search_fields = ['recipient__username', 'title']
    list_editable = ['is_read']


@admin.register(AIAnalysisLog)
class AIAnalysisLogAdmin(admin.ModelAdmin):
    list_display  = ['assignment', 'analysis_type', 'score', 'created_at']
    list_filter   = ['analysis_type']
    readonly_fields = ['result', 'created_at']

from assessment.models import QuestionBank, BankQuestion

class BankQuestionInline(admin.TabularInline):
    model   = BankQuestion
    extra   = 0
    fields  = ['text', 'correct_answer', 'option_a', 'option_b', 'option_c', 'topic', 'difficulty', 'use_count', 'is_duplicate']
    readonly_fields = ['use_count', 'is_duplicate']

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display  = ['title', 'teacher', 'subject', 'questions_count', 'updated_at']
    list_filter   = ['subject__department']
    search_fields = ['title', 'teacher__username']
    inlines       = [BankQuestionInline]
    def questions_count(self, obj): return obj.questions_count
    questions_count.short_description = "Savollar"
