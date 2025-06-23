from rest_framework import viewsets, permissions, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Lesson, Enrollment, Instructor, VideoProgress
from .serializers import (
    CourseSerializer, CourseCreateSerializer, LessonSerializer, 
    EnrollmentSerializer, InstructorSerializer, VideoProgressSerializer
)

class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_instructor

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.instructor == request.user

class IsInstructorForLessons(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_instructor

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsInstructorOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise permissions.PermissionDenied("Authentication required")
        
        if not hasattr(self.request.user, 'profile') or not self.request.user.profile.is_instructor:
            raise permissions.PermissionDenied("Only instructors can create courses")
        
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        courses = Course.objects.filter(instructor=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorForLessons]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise permissions.PermissionDenied("Authentication required")
        
        if not hasattr(self.request.user, 'profile') or not self.request.user.profile.is_instructor:
            raise permissions.PermissionDenied("Only instructors can create lessons")
        
        # Get the course and check if the user is the instructor
        course_id = self.request.data.get('course')
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                if course.instructor != self.request.user:
                    raise permissions.PermissionDenied("You can only add lessons to your own courses")
            except Course.DoesNotExist:
                raise permissions.PermissionDenied("Course not found")
        
        serializer.save()

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            instructor = Instructor.objects.get(user=request.user)
            serializer = InstructorSerializer(instructor)
            return Response(serializer.data)
        except Instructor.DoesNotExist:
            return Response({'error': 'Instructor profile not found'}, status=status.HTTP_404_NOT_FOUND)

class VideoProgressViewSet(viewsets.ModelViewSet):
    queryset = VideoProgress.objects.all()
    serializer_class = VideoProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VideoProgress.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        lesson = serializer.validated_data['lesson']
        # Check if user is enrolled in the course of the lesson
        if not Enrollment.objects.filter(student=self.request.user, course=lesson.course).exists():
            raise permissions.PermissionDenied("You are not enrolled in this course.")
        
        # Update or create progress
        progress, created = VideoProgress.objects.update_or_create(
            student=self.request.user,
            lesson=lesson,
            defaults={'last_watched_timestamp': serializer.validated_data['last_watched_timestamp']}
        )
        serializer.instance = progress
        
    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        lesson_id = request.data.get('lesson')
        timestamp = request.data.get('last_watched_timestamp')

        if not lesson_id or timestamp is None:
            return Response({'error': 'Lesson and timestamp are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
            return Response({'error': 'You are not enrolled in this course.'}, status=status.HTTP_403_FORBIDDEN)

        progress, created = VideoProgress.objects.update_or_create(
            student=request.user,
            lesson=lesson,
            defaults={'last_watched_timestamp': timestamp}
        )

        serializer = VideoProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
