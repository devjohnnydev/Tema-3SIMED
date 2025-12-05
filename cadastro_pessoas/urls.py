# cadastro_pessoas/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # URLs do allauth (Google OAuth)
    path('', include('pessoas.urls')),  # URLs do app pessoas
]

# Servir arquivos de mídia em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
