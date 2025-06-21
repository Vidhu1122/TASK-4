from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CourseViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollments')

urlpatterns = [
    path('', include(router.urls)),
]
# The above code sets up the URL routing for the courses app in a Django project.
# It uses Django REST Framework's DefaultRouter to automatically generate the URL patterns for the CourseViewSet and EnrollmentViewSet.