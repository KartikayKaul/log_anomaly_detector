from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Pages
    path('', views.dashboard, name='home'),
    path('testing/', views.testing, name='testing'),
    path('config/', views.config_page, name='config'),

#     path("generate-logs/", views.generate_logs, name="generate_logs"),
# path("save-config/", views.save_config, name="save_config"),
# path("download-config/", views.download_config, name="download_config"),

    # APIs
    path('api/detect/', api.detect_log_api, name='detect_log_api'),
    path('api/detect-file/', api.detect_file_api, name='detect_file_api'),

    path("download/<str:file_type>/", views.download_generated_file, name="download_generated_file")
]