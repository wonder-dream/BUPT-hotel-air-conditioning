"""
URL configuration for hotel_ac project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("ac_system.urls")),
]
