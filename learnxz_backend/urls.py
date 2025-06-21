"""
URL configuration for learnxz_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# learnxz_backend/learnxz_backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('courses.urls')),  # ✅ API routes from courses app
    path('api-auth/', include('rest_framework.urls')),  # Optional: DRF login for browsable API
    path('auth/', include('djoser.urls')),  # User registration and management
    path('auth/', include('djoser.urls.authtoken')),  # Token authentication
]

# The above code sets up the URL routing for the Django project, including the admin interface, API endpoints for courses, and authentication routes using Djoser.
# This allows the application to handle requests for course management and user authentication seamlessly.
