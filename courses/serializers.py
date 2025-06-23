from rest_framework import serializers
from .models import Course, Lesson, Enrollment, Instructor, VideoProgress
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class InstructorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Instructor
        fields = '__all__'

class VideoProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProgress
        fields = ['lesson', 'last_watched_timestamp']

class LessonSerializer(serializers.ModelSerializer):
    video = serializers.FileField(required=False)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = '__all__'
    
    def get_progress(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                progress = VideoProgress.objects.get(student=user, lesson=obj)
                return VideoProgressSerializer(progress).data
            except VideoProgress.DoesNotExist:
                return None
        return None

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    instructor = UserSerializer(read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lesson_count(self, obj):
        return obj.lessons.count()

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'is_published']

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_instructor = serializers.CharField(source='course.instructor.username', read_only=True)
    course_price = serializers.CharField(source='course.price', read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_on', 'course_title', 'course_instructor', 'course_price']
