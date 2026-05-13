from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
import json

from accounts.models import User
from core.models import Department, Subject, SubjectTeacher
from assessment.models import Assignment, Question, Submission, AIAnalysisLog


def role_required(*roles):
    def decorator(fn):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, "Ruxsat yo'q.")
                return redirect(request.user.get_dashboard_url())
            return fn(request, *args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator


# ─── KAFEDRA ANALITIKASI ────────────────────────────
@role_required('kafedra_mudiri')
def kafedra_analytics(request):
    dept = request.user.department
    if not dept:
        from django.contrib import messages
        messages.warning(request, "Kafedraga biriktirilmagansiz. Administrator bilan bog'laning.")
        return render(request, 'analytics/kafedra_analytics.html', {
            'dept': None,
            'months': [], 'months_json': '[]',
            'teachers': [], 'subjects': [],
            'topic_stats': [], 'ai_excellent': 0, 'ai_good': 0, 'ai_poor': 0,
            'total_ai': 0, 'unread_count': request.user.notifications.filter(is_read=False).count(),
        })

    # Oy bo'yicha topshiriqlar va javoblar (so'nggi 6 oy)
    now    = timezone.now()
    months = []
    for i in range(5, -1, -1):
        d = now - timedelta(days=30 * i)
        months.append({
            'label': d.strftime('%b %Y'),
            'assignments': Assignment.objects.filter(
                subject__department=dept,
                created_at__year=d.year, created_at__month=d.month
            ).count(),
            'submissions': Submission.objects.filter(
                assignment__subject__department=dept,
                submitted_at__year=d.year, submitted_at__month=d.month
            ).count(),
        })

    # O'qituvchilar reytingi (sillabus moslik bali bo'yicha)
    teachers = User.objects.filter(role='oqituvchi', department=dept).annotate(
        avg_ai=Avg('created_assignments__ai_syllabus_score'),
        total_assignments=Count('created_assignments'),
        graded_count=Count('created_assignments__submissions', filter=Q(
            created_assignments__submissions__status='graded')),
    ).order_by('-avg_ai')

    # Fanlar bo'yicha o'rtacha ball
    subjects = Subject.objects.filter(department=dept).annotate(
        avg_score=Avg('assignments__submissions__final_score'),
        total_subs=Count('assignments__submissions'),
    ).order_by('-avg_score')

    # Mavzular bo'yicha xato thlili
    wrong_topics = {}
    questions = Question.objects.filter(
        assignment__subject__department=dept
    ).select_related('assignment')
    for q in questions:
        topic = q.topic or "Noma'lum"
        if topic not in wrong_topics:
            wrong_topics[topic] = {'total': 0, 'wrong': 0}
        for sub in q.assignment.submissions.all():
            if sub.test_answers:
                wrong_topics[topic]['total'] += 1
                ans = sub.test_answers.get(str(q.pk), '')
                if ans.upper() != q.correct_answer.upper():
                    wrong_topics[topic]['wrong'] += 1

    topic_stats = [
        {
            'topic': t,
            'total': v['total'],
            'wrong': v['wrong'],
            'pct': round(v['wrong'] / v['total'] * 100, 1) if v['total'] else 0
        }
        for t, v in wrong_topics.items() if v['total'] > 0
    ]
    topic_stats.sort(key=lambda x: x['pct'], reverse=True)

    # AI sillabus tekshiruv statistikasi
    ai_logs_qs = AIAnalysisLog.objects.filter(
        assignment__subject__department=dept,
        analysis_type='syllabus_check'
    ).select_related('assignment__teacher').order_by('-created_at')

    excellent = ai_logs_qs.filter(score__gte=85).count()
    good      = ai_logs_qs.filter(score__gte=65, score__lt=85).count()
    poor      = ai_logs_qs.filter(score__lt=65).count()
    ai_logs   = ai_logs_qs[:20]

    ctx = {
        'dept': dept,
        'months': months,
        'months_json': json.dumps(months),
        'teachers': teachers[:10],
        'subjects': subjects,
        'topic_stats': topic_stats[:10],
        'ai_excellent': excellent,
        'ai_good': good,
        'ai_poor': poor,
        'total_ai': excellent + good + poor,
        'unread_count': request.user.notifications.filter(is_read=False).count(),
    }
    return render(request, 'analytics/kafedra_analytics.html', ctx)


# ─── O'QITUVCHI ANALITIKASI ─────────────────────────
@role_required('oqituvchi')
def teacher_analytics(request):
    t   = request.user
    now = timezone.now()

    # So'nggi 6 oy faolligi
    months = []
    for i in range(5, -1, -1):
        d = now - timedelta(days=30 * i)
        months.append({
            'label': d.strftime('%b'),
            'assignments': Assignment.objects.filter(
                teacher=t, created_at__year=d.year, created_at__month=d.month).count(),
            'submissions': Submission.objects.filter(
                assignment__teacher=t,
                submitted_at__year=d.year, submitted_at__month=d.month).count(),
        })

    # Fan bo'yicha o'rtacha ball
    my_subjects = SubjectTeacher.objects.filter(teacher=t).select_related('subject').annotate(
        avg_score=Avg('subject__assignments__submissions__final_score',
                      filter=Q(subject__assignments__teacher=t)),
        total_subs=Count('subject__assignments__submissions',
                         filter=Q(subject__assignments__teacher=t)),
    )

    # Talaba baholari taqsimoti
    subs = Submission.objects.filter(
        assignment__teacher=t, final_score__isnull=False
    )
    grade_dist = {
        'A+': subs.filter(final_score__gte=91).count(),
        'A':  subs.filter(final_score__gte=86, final_score__lt=91).count(),
        'B+': subs.filter(final_score__gte=76, final_score__lt=86).count(),
        'B':  subs.filter(final_score__gte=66, final_score__lt=76).count(),
        'C':  subs.filter(final_score__gte=50, final_score__lt=66).count(),
        'F':  subs.filter(final_score__lt=50).count(),
    }

    # AI sillabus tekshiruv o'rtachasi
    avg_ai = Assignment.objects.filter(
        teacher=t, ai_syllabus_score__isnull=False
    ).aggregate(avg=Avg('ai_syllabus_score'))['avg']

    ctx = {
        'months_json': json.dumps(months),
        'my_subjects': my_subjects,
        'grade_dist': grade_dist,
        'grade_dist_json': json.dumps(grade_dist),
        'avg_ai_score': round(avg_ai, 1) if avg_ai else None,
        'total_graded': subs.count(),
        'unread_count': t.notifications.filter(is_read=False).count(),
    }
    return render(request, 'analytics/teacher_analytics.html', ctx)


# ─── TALABA ANALITIKASI ─────────────────────────────
@role_required('talaba')
def student_analytics(request):
    s   = request.user
    subs = Submission.objects.filter(student=s, final_score__isnull=False).select_related(
        'assignment__subject'
    ).order_by('submitted_at')

    # Vaqt bo'yicha dinamika
    trend = [{
        'label': sub.submitted_at.strftime('%d.%m'),
        'score': sub.final_score,
        'subject': sub.assignment.subject.name,
    } for sub in subs]

    # Fan bo'yicha statistika
    by_subject = {}
    for sub in subs:
        name = sub.assignment.subject.name
        if name not in by_subject:
            by_subject[name] = []
        by_subject[name].append(sub.final_score)

    subject_stats = [{
        'name': name,
        'avg': round(sum(scores) / len(scores), 1),
        'max': max(scores),
        'min': min(scores),
        'count': len(scores),
    } for name, scores in by_subject.items()]
    subject_stats.sort(key=lambda x: x['avg'], reverse=True)

    ctx = {
        'trend_json': json.dumps(trend),
        'subject_stats': subject_stats,
        'subject_stats_json': json.dumps(subject_stats),
        'total_completed': subs.count(),
        'overall_avg': round(
            sum(s['avg'] for s in subject_stats) / len(subject_stats), 1
        ) if subject_stats else None,
        'best_subject': subject_stats[0] if subject_stats else None,
        'weak_subject': subject_stats[-1] if len(subject_stats) > 1 else None,
        'unread_count': s.notifications.filter(is_read=False).count(),
    }
    return render(request, 'analytics/student_analytics.html', ctx)


# ─── ADMIN ANALITIKASI ──────────────────────────────
@role_required('admin')
def admin_analytics(request):
    now = timezone.now()
    months = []
    for i in range(5, -1, -1):
        d = now - timedelta(days=30 * i)
        months.append({
            'label': d.strftime('%b %Y'),
            'users': User.objects.filter(
                date_joined__year=d.year, date_joined__month=d.month).count(),
            'assignments': Assignment.objects.filter(
                created_at__year=d.year, created_at__month=d.month).count(),
        })

    ctx = {
        'months_json': json.dumps(months),
        'total_users': User.objects.count(),
        'total_assignments': Assignment.objects.count(),
        'total_submissions': Submission.objects.count(),
        'avg_score': round(
            Submission.objects.filter(final_score__isnull=False).aggregate(
                a=Avg('final_score'))['a'] or 0, 1),
        'departments': Department.objects.annotate(
            teacher_count=Count('staff', filter=Q(staff__role='oqituvchi')),
            student_count=Count('groups__students'),
            avg=Avg('subjects__assignments__submissions__final_score'),
        ),
        'unread_count': request.user.notifications.filter(is_read=False).count(),
    }
    return render(request, 'analytics/admin_analytics.html', ctx)


# ─── JSON API ─────────────────────────────────────────
@login_required
def analytics_api(request):
    """AJAX uchun statistika JSON"""
    dtype = request.GET.get('type', '')
    user  = request.user

    if dtype == 'submissions_by_day' and user.is_teacher:
        now  = timezone.now()
        data = []
        for i in range(6, -1, -1):
            d = now - timedelta(days=i)
            data.append({
                'day': d.strftime('%a'),
                'count': Submission.objects.filter(
                    assignment__teacher=user,
                    submitted_at__date=d.date()
                ).count()
            })
        return JsonResponse({'data': data})

    if dtype == 'grade_distribution' and user.is_teacher:
        subs = Submission.objects.filter(
            assignment__teacher=user, final_score__isnull=False)
        return JsonResponse({'data': {
            'A+': subs.filter(final_score__gte=91).count(),
            'A':  subs.filter(final_score__gte=86, final_score__lt=91).count(),
            'B':  subs.filter(final_score__gte=66, final_score__lt=86).count(),
            'C':  subs.filter(final_score__gte=50, final_score__lt=66).count(),
            'F':  subs.filter(final_score__lt=50).count(),
        }})

    return JsonResponse({'error': 'Unknown type'}, status=400)
