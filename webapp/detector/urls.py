from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Pages
    path('', views.dashboard, name='home'),
    path('testing/', views.testing, name='testing'),
    path('config/', views.config_page, name='config'),
    path('wipe-logs/', views.wipe_logs, name='wipe_logs'),


    # APIs
    path('api/detect/', api.detect_log_api, name='detect_log_api'),
    path('api/detect-file/', api.detect_file_api, name='detect_file_api'),

    path("download/<str:file_type>/", views.download_generated_file, name="download_generated_file")
]