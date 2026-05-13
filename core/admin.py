from django.contrib import admin
from .models import Department, Group, Subject, SubjectTeacher, ExamSchedule


class GroupInline(admin.TabularInline):
    model = Group
    extra = 1
    fields = ['name', 'year']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ['name', 'code', 'teachers_count', 'students_count', 'created_at']
    search_fields = ['name', 'code']
    inlines       = [GroupInline]

    def teachers_count(self, obj): return obj.teachers_count
    teachers_count.short_description = "O'qituvchilar"

    def students_count(self, obj): return obj.students_count
    students_count.short_description = "Talabalar"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display  = ['name', 'department', 'year', 'students_count']
    list_filter   = ['department', 'year']
    search_fields = ['name']

    def students_count(self, obj): return obj.students_count
    students_count.short_description = "Talabalar soni"


class SubjectTeacherInline(admin.TabularInline):
    model  = SubjectTeacher
    extra  = 1
    fields = ['teacher', 'groups']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ['name', 'code', 'department', 'credits', 'semester']
    list_filter   = ['department', 'semester']
    search_fields = ['name', 'code']
    inlines       = [SubjectTeacherInline]


@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'assigned_at']
    list_filter  = ['subject__department']
    filter_horizontal = ['groups']


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display  = ['subject', 'department', 'exam_date', 'room', 'days_remaining']
    list_filter   = ['department']
    filter_horizontal = ['groups']

    def days_remaining(self, obj):
        d = obj.days_remaining
        return f"{d} kun" if d >= 0 else "O'tdi"
    days_remaining.short_description = "Qolgan kunlar"
