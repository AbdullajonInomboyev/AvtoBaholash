from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    # PDF export
    path('pdf/<int:pk>/', views.download_pdf, name='download_pdf'),
    # Excel export (teacher)
    path('export/xlsx/<int:pk>/', views.export_xlsx, name='export_xlsx'),
    # Word template download
    path('template/test/', views.download_test_template, name='test_template'),
    path('template/written/', views.download_written_template, name='written_template'),
    # Telegram webhook
    path('webhook/telegram/', views.telegram_webhook, name='telegram_webhook'),
]
