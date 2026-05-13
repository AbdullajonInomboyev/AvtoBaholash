from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('core.urls', namespace='core')),
    path('assessment/', include('assessment.urls', namespace='assessment')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('', lambda r: redirect('dashboard/')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
