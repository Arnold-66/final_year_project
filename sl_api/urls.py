# urls.py
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse
import json
import os
from django.conf import settings
import time

# urls.py - update the cwaclientcfg_view function
# urls.py - add this
from django.http import JsonResponse
import json

def cwaclientcfg_view(request):
    """Serve cwaclientcfg.json"""
    config_path = os.path.join(settings.STATIC_ROOT, 'cwaclientcfg.json')
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        # Fallback config
        config = {
            "description": "CWA Configuration",
            "signingAvatarCfg": "/static/cwa/signingavatar/signingavatar_config.xml",
            "signingAvatarDir": "/static/cwa/signingavatar",
            "signingAvatarURL": "/static/cwa/signingavatar",
            "useProxy": False,
            "avatar": {
                "default": "anna",
                "available": ["anna", "pablo", "marc"],
                "baseURL": "/static/avatars/",
                "jarURL": "/static/avatars/",
                "xmlURL": "/static/avatars/",
                "mappings": {
                    "anna": {"jar": "anna.jar", "xml": "anna.xml"},
                    "pablo": {"jar": "pablo.jar", "xml": "pablo.xml"},
                    "marc": {"jar": "marc.jar", "xml": "marc.xml"}
                }
            },
            "useLocalAvatar": True,
            "localAvatarPath": "/static/avatars",
            "crossOrigin": False
        }
    
    return JsonResponse(config)

# Add to urlpatterns
urlpatterns = [
    path('cwaclientcfg.json', cwaclientcfg_view, name='cwaclientcfg'),
    
    path('', views.frontend_view, name='frontend'),
    
    # CWA Configuration - MUST BE AT ROOT LEVEL
    path('cwaclientcfg.json', cwaclientcfg_view, name='cwaclientcfg'),
    
    # API Endpoints
    path('api/signs/', views.SignListAPIView.as_view(), name='sign-list'),
    path('api/signs/<str:word>/', views.SignDetailAPIView.as_view(), name='sign-detail'),
    path('api/signs/upload/', views.SignUploadAPIView.as_view(), name='sign-upload'),
    path('api/debug/', views.debug_api, name='api-debug'),
    path('api/signs/public/upload/', views.PublicSignUploadView.as_view(), name='public-sign-upload'),
     path('api/set-avatar/', views.set_avatar, name='set-avatar'),
    path('api/get-avatar/', views.get_avatar, name='get-avatar'),
    
    # Other paths
    path('bulk-upload/', TemplateView.as_view(template_name='bulk_upload.html'), name='bulk_upload'),
    path('api/bulk-upload/', views.BulkSignUploadView.as_view(), name='bulk_upload_api'),
    path('api/generate-categories/', views.GenerateCategoriesView.as_view(), name='generate_categories'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    