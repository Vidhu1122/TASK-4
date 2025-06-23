from django.contrib import admin
from .models import Course, Lesson, Enrollment, Instructor

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'created_at')
    list_filter = ('created_at', 'expertise')
    search_fields = ('user__username', 'user__email', 'expertise')
    date_hierarchy = 'created_at'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'is_published', 'created_at')
    list_filter = ('created_at', 'price', 'is_published')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'video_url')
    list_filter = ('course', 'order')
    search_fields = ('title', 'content')
    ordering = ('course', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_on')
    list_filter = ('enrolled_on', 'course')
    search_fields = ('student__username', 'course__title')
    date_hierarchy = 'enrolled_on'
