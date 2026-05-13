"""
AvtoBaholash — Assessment app unit testlar
python manage.py test assessment
"""
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from core.models import Department, Group, Subject, SubjectTeacher
from assessment.models import (
    Assignment, Question, Submission, Syllabus,
    Feedback, Notification, QuestionBank, BankQuestion
)


class BaseTestCase(TestCase):
    """Barcha testlar uchun umumiy setup"""
    def setUp(self):
        self.dept = Department.objects.create(name='Test Kafedra', code='TST')
        self.group = Group.objects.create(name='TST-101', department=self.dept)
        self.subject = Subject.objects.create(
            name='Test Fan', code='TF101', department=self.dept)
        # Users
        self.admin    = User.objects.create_user('test_admin', password='pass123', role='admin', is_staff=True, is_superuser=True)
        self.kafedra  = User.objects.create_user('test_kafedra', password='pass123', role='kafedra_mudiri', department=self.dept)
        self.teacher  = User.objects.create_user('test_teacher', password='pass123', role='oqituvchi', department=self.dept)
        self.student  = User.objects.create_user('test_student', password='pass123', role='talaba', group=self.group)
        # SubjectTeacher
        self.st = SubjectTeacher.objects.create(subject=self.subject, teacher=self.teacher)
        self.st.groups.add(self.group)


class ModelTestCase(BaseTestCase):
    """Model metodlarini tekshirish"""

    def test_user_roles(self):
        self.assertTrue(self.admin.is_admin)
        self.assertTrue(self.kafedra.is_kafedra)
        self.assertTrue(self.teacher.is_teacher)
        self.assertTrue(self.student.is_student)

    def test_user_full_name(self):
        self.teacher.first_name = 'Mansur'
        self.teacher.last_name  = 'Karimov'
        self.teacher.save()
        self.assertEqual(self.teacher.full_name, 'Karimov Mansur')

    def test_user_initials(self):
        self.teacher.first_name = 'Mansur'
        self.teacher.last_name  = 'Karimov'
        self.teacher.save()
        self.assertEqual(self.teacher.initials, 'KM')

    def test_user_dashboard_url(self):
        """Admin endi /dashboard/admin-panel/ ga yo'naltiriladi"""
        self.assertEqual(self.admin.get_dashboard_url(),   '/dashboard/admin-panel/')
        self.assertEqual(self.kafedra.get_dashboard_url(), '/dashboard/kafedra/')
        self.assertEqual(self.teacher.get_dashboard_url(), '/dashboard/teacher/')
        self.assertEqual(self.student.get_dashboard_url(), '/dashboard/student/')

    def test_assignment_is_open(self):
        a = Assignment.objects.create(
            title='Test', assignment_type='test',
            subject=self.subject, teacher=self.teacher,
            deadline=timezone.now() + timedelta(days=3),
            status='active'
        )
        self.assertTrue(a.is_open)
        self.assertFalse(a.is_expired)

    def test_assignment_is_expired(self):
        a = Assignment.objects.create(
            title='Past', assignment_type='test',
            subject=self.subject, teacher=self.teacher,
            deadline=timezone.now() - timedelta(days=1),
            status='active'
        )
        self.assertFalse(a.is_open)
        self.assertTrue(a.is_expired)

    def test_submission_grade_letter(self):
        """5 ballik tizim: 5=86-100, 4=71-85, 3=56-70, 2=41-55, 1=0-40"""
        a = Assignment.objects.create(
            title='T', assignment_type='test', subject=self.subject,
            teacher=self.teacher, deadline=timezone.now() + timedelta(days=1))
        sub = Submission.objects.create(assignment=a, student=self.student, final_score=95)
        self.assertEqual(sub.grade_letter, '5')
        sub.final_score = 80
        self.assertEqual(sub.grade_letter, '4')
        sub.final_score = 63
        self.assertEqual(sub.grade_letter, '3')
        sub.final_score = 48
        self.assertEqual(sub.grade_letter, '2')
        sub.final_score = 30
        self.assertEqual(sub.grade_letter, '1')

    def test_question_bank_creation(self):
        bank = QuestionBank.objects.create(
            teacher=self.teacher, subject=self.subject, title='Test Bank')
        BankQuestion.objects.create(
            bank=bank, text='Savol?', correct_answer='A',
            option_a='Ha', option_b='Yo\'q', option_c='Balki')
        self.assertEqual(bank.questions_count, 1)

    def test_department_properties(self):
        self.assertEqual(self.dept.teachers_count, 1)
        self.assertEqual(self.dept.students_count, 1)


class AuthViewTestCase(BaseTestCase):
    """Login/Logout viewlarini tekshirish"""

    def test_login_page_loads(self):
        r = self.client.get('/auth/login/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'AvtoBaholash')

    def test_login_success(self):
        r = self.client.post('/auth/login/', {'username': 'test_admin', 'password': 'pass123'})
        self.assertEqual(r.status_code, 302)

    def test_login_failure(self):
        r = self.client.post('/auth/login/', {'username': 'test_admin', 'password': 'wrong'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'noto&#x27;g&#x27;ri')  # HTML escaped apostrophe

    def test_logout(self):
        self.client.login(username='test_admin', password='pass123')
        r = self.client.get('/auth/logout/')
        self.assertEqual(r.status_code, 302)


class RoleAccessTestCase(BaseTestCase):
    """Rol asosida kirish huquqlarini tekshirish"""

    def _login(self, user):
        self.client.login(username=user.username, password='pass123')

    def test_admin_can_access_admin_pages(self):
        self._login(self.admin)
        # /dashboard/ endi dashboard_router orqali /dashboard/admin-panel/ ga redirect
        r = self.client.get('/dashboard/')
        self.assertIn(r.status_code, [200, 302], "/dashboard/ should redirect or show")
        # Admin-specific pages
        for url in ['/dashboard/admin-panel/', '/dashboard/admin/departments/', '/dashboard/admin/users/']:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200, f"{url} failed")

    def test_teacher_redirected_from_admin(self):
        self._login(self.teacher)
        r = self.client.get('/dashboard/')
        self.assertEqual(r.status_code, 302)  # redirect to teacher dashboard

    def test_student_cant_access_teacher_pages(self):
        self._login(self.student)
        r = self.client.get('/dashboard/teacher/')
        self.assertIn(r.status_code, [302, 403])

    def test_unauthenticated_redirected(self):
        r = self.client.get('/dashboard/teacher/')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/auth/login/', r['Location'])

    def test_kafedra_dashboard_loads(self):
        self._login(self.kafedra)
        r = self.client.get('/dashboard/kafedra/')
        self.assertEqual(r.status_code, 200)

    def test_teacher_dashboard_loads(self):
        self._login(self.teacher)
        r = self.client.get('/dashboard/teacher/')
        self.assertEqual(r.status_code, 200)

    def test_student_dashboard_loads(self):
        self._login(self.student)
        r = self.client.get('/dashboard/student/')
        self.assertEqual(r.status_code, 200)


class AssignmentFlowTestCase(BaseTestCase):
    """Topshiriq yaratish va test topshirish oqimi"""

    def setUp(self):
        super().setUp()
        self.assignment = Assignment.objects.create(
            title='Algoritm testi',
            assignment_type='test',
            subject=self.subject,
            teacher=self.teacher,
            deadline=timezone.now() + timedelta(days=7),
            status='active',
        )
        self.assignment.groups.add(self.group)
        self.q1 = Question.objects.create(
            assignment=self.assignment, text='2+2=?',
            correct_answer='A', option_a='4', option_b='3', option_c='5', order=1)
        self.q2 = Question.objects.create(
            assignment=self.assignment, text='3*3=?',
            correct_answer='C', option_a='6', option_b='8', option_c='9', order=2)

    def test_student_can_see_test(self):
        self.client.login(username='test_student', password='pass123')
        r = self.client.get(f'/dashboard/student/submit/{self.assignment.pk}/')
        self.assertEqual(r.status_code, 200)

    def test_student_submits_test(self):
        self.client.login(username='test_student', password='pass123')
        data = {
            f'ans_{self.q1.pk}': 'A',
            f'ans_{self.q2.pk}': 'C',
            'tab_switches': '0',
            'time_taken': '120',
        }
        r = self.client.post(f'/dashboard/student/submit/{self.assignment.pk}/', data)
        self.assertEqual(r.status_code, 302)
        sub = Submission.objects.get(assignment=self.assignment, student=self.student)
        self.assertEqual(sub.ai_score, 100.0)

    def test_student_cannot_resubmit(self):
        Submission.objects.create(
            assignment=self.assignment, student=self.student, status='submitted')
        self.client.login(username='test_student', password='pass123')
        r = self.client.get(f'/dashboard/student/submit/{self.assignment.pk}/')
        self.assertEqual(r.status_code, 302)

    def test_teacher_edit_assignment_loads(self):
        self.client.login(username='test_teacher', password='pass123')
        r = self.client.get(f'/dashboard/teacher/assignments/{self.assignment.pk}/edit/')
        self.assertEqual(r.status_code, 200)

    def test_grade_book_loads(self):
        self.client.login(username='test_teacher', password='pass123')
        r = self.client.get(f'/dashboard/teacher/grade-book/?subject={self.subject.pk}&assignment={self.assignment.pk}')
        self.assertEqual(r.status_code, 200)


class AIServiceTestCase(TestCase):
    """AI servis funksiyalarini tekshirish (demo rejim)"""

    def test_grade_test_no_answers(self):
        from assessment.services.ai_service import grade_test
        result = grade_test('Test', [])
        self.assertEqual(result['score'], 0)

    def test_grade_test_all_correct(self):
        from assessment.services.ai_service import grade_test
        qwa = [{'text': 'Q1', 'correct_answer': 'A', 'student_answer': 'A'} for _ in range(5)]
        result = grade_test('Test', qwa)
        self.assertEqual(result['score'], 100.0)
        self.assertEqual(result['correct_count'], 5)

    def test_grade_test_all_wrong(self):
        from assessment.services.ai_service import grade_test
        qwa = [{'text': 'Q', 'correct_answer': 'A', 'student_answer': 'B'} for _ in range(4)]
        result = grade_test('Test', qwa)
        self.assertEqual(result['score'], 0.0)
        self.assertEqual(result['correct_count'], 0)

    def test_grade_test_half_correct(self):
        from assessment.services.ai_service import grade_test
        qwa = [
            {'text': 'Q1', 'correct_answer': 'A', 'student_answer': 'A'},
            {'text': 'Q2', 'correct_answer': 'B', 'student_answer': 'A'},
        ]
        result = grade_test('Test', qwa)
        self.assertEqual(result['score'], 50.0)

    def test_check_syllabus_no_api(self):
        from assessment.services.ai_service import check_syllabus_compliance
        result = check_syllabus_compliance('Test', 'Desc', 'Q1\nQ2', ['Mavzu1', 'Mavzu2'])
        self.assertIn('score', result)
        self.assertIn('feedback', result)

    def test_send_notification(self):
        user = User.objects.create_user('notif_user', password='p', role='talaba')
        from assessment.services.ai_service import send_notification
        send_notification(user, 'Test', 'Xabar', 'info')
        self.assertEqual(Notification.objects.filter(recipient=user).count(), 1)


class ExportServiceTestCase(BaseTestCase):
    """Export servislarini tekshirish"""

    def setUp(self):
        super().setUp()
        self.assignment = Assignment.objects.create(
            title='Export Test', assignment_type='test',
            subject=self.subject, teacher=self.teacher,
            deadline=timezone.now() + timedelta(days=1))
        Question.objects.create(
            assignment=self.assignment, text='Savol?',
            correct_answer='A', option_a='Ha', option_b='Yo\'q', option_c='Balki')

    def test_pdf_endpoint(self):
        self.client.login(username='test_teacher', password='pass123')
        r = self.client.get(f'/assessment/pdf/{self.assignment.pk}/')
        self.assertEqual(r.status_code, 200)

    def test_word_test_template(self):
        self.client.login(username='test_teacher', password='pass123')
        r = self.client.get('/assessment/template/test/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('wordprocessingml', r['Content-Type'])

    def test_word_written_template(self):
        self.client.login(username='test_teacher', password='pass123')
        r = self.client.get('/assessment/template/written/')
        self.assertEqual(r.status_code, 200)

    def test_excel_export(self):
        Submission.objects.create(
            assignment=self.assignment, student=self.student,
            final_score=85.0, status='graded')
        self.client.login(username='test_teacher', password='pass123')
        r = self.client.get(f'/assessment/export/xlsx/{self.assignment.pk}/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('spreadsheet', r['Content-Type'])
