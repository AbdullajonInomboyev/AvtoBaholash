from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Router
    path('', views.dashboard_router, name='dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    # Admin
    path('admin/departments/',              views.admin_departments,        name='admin_departments'),
    path('admin/departments/<int:pk>/',     views.admin_department_detail,  name='admin_department_detail'),
    path('admin/users/',                    views.admin_users,              name='admin_users'),
    path('admin-panel/users/<int:pk>/edit/', views.admin_edit_user,         name='admin_edit_user'),
    path('admin/subjects/',                 views.admin_subjects,           name='admin_subjects'),
    path('admin/reports/',                  views.admin_reports,            name='admin_reports'),
    path('admin/settings/',                 views.admin_settings,           name='admin_settings'),

    # Kafedra mudiri
    path('kafedra/',                        views.kafedra_dashboard,        name='kafedra_dashboard'),
    path('kafedra/teachers/',               views.kafedra_teachers,         name='kafedra_teachers'),
    path('kafedra/students/',               views.kafedra_students,         name='kafedra_students'),
    path('kafedra/students/<int:pk>/edit/', views.kafedra_edit_student,     name='kafedra_edit_student'),
    path('kafedra/subjects/',               views.kafedra_subjects,         name='kafedra_subjects'),
    path('kafedra/exams/',                  views.kafedra_exam_schedule,    name='kafedra_exam_schedule'),
    path('kafedra/exams/<int:pk>/',         views.kafedra_exam_detail,      name='kafedra_exam_detail'),
    path('kafedra/ai-journal/',             views.kafedra_ai_journal,       name='kafedra_ai_journal'),

    # O'qituvchi
    path('teacher/',                                    views.teacher_dashboard,         name='teacher_dashboard'),
    path('teacher/subjects/',                           views.teacher_subjects,          name='teacher_subjects'),
    path('teacher/subjects/<int:subject_id>/syllabus/', views.teacher_upload_syllabus,   name='teacher_upload_syllabus'),
    path('teacher/assignments/',                        views.teacher_assignments,       name='teacher_assignments'),
    path('teacher/assignments/create/',                 views.teacher_create_assignment, name='teacher_create_assignment'),
    path('teacher/assignments/<int:pk>/edit/',          views.teacher_edit_assignment,   name='teacher_edit_assignment'),
    path('teacher/assignments/<int:pk>/quota/',         views.teacher_topic_quota,       name='teacher_topic_quota'),
    path('teacher/questions/<int:pk>/edit/',            views.teacher_edit_question,     name='teacher_edit_question'),
    path('teacher/grade-book/',                         views.teacher_grade_book,        name='teacher_grade_book'),
    path('teacher/feedback/',                           views.teacher_feedback,          name='teacher_feedback'),
    path('teacher/appeal/<int:sub_pk>/review/',         views.review_appeal,             name='review_appeal'),
    path('teacher/question-banks/',                     views.teacher_question_banks,    name='teacher_question_banks'),
    path('teacher/question-banks/<int:pk>/',            views.teacher_bank_detail,       name='teacher_bank_detail'),

    # Talaba
    path('student/',                        views.student_dashboard,    name='student_dashboard'),
    path('student/assignments/',            views.student_assignments,  name='student_assignments'),
    path('student/submit/<int:pk>/',        views.student_submit,       name='student_submit'),
    path('student/result/<int:pk>/',        views.student_result,       name='student_result'),
    path('student/progress/',               views.student_progress,     name='student_progress'),
    path('student/appeal/<int:sub_pk>/',    views.submit_appeal,        name='submit_appeal'),

    # Excel import
    path('import/students/',                views.import_students_excel,    name='import_students_excel'),
    path('import/students/template/',       views.download_student_template,name='student_import_template'),

    # Umumiy
    path('notifications/',                  views.notifications,        name='notifications'),
    path('notifications/<int:pk>/read/',    views.mark_read,            name='mark_read'),
    path('tts/',                            views.tts_audio,            name='tts_audio'),
    path('toggle-accessible/<int:pk>/',     views.toggle_accessible,    name='toggle_accessible'),
]