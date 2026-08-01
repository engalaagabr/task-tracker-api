from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer, RegisterSerializer

from rest_framework import status, permissions

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.generics import get_object_or_404

from django.http import Http404

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    # 1. Enable the three core filter engines: Exact Filtering, Text Search, and Result Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # 2. Fields allowed for exact match filtering 
    filterset_fields = ['status', 'priority']

    # 3. Text fields that will be scanned during substring searches 
    search_fields = ['title', 'description']

    # 4. Fields allowed for client-side sorting 
    ordering_fields = ['due_date', 'created_at', 'priority']

    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')

        if not Project.objects.filter(id=project_pk, owner=self.request.user).exists():
            raise Http404("Project not found or access denied")
          
        return Task.objects.filter(
            project_id=project_pk,
            project__owner=self.request.user  # IDOR protection
        )

    def perform_create(self, serializer):
        project = get_object_or_404(
            Project, 
            id=self.kwargs['project_pk'], 
            owner=self.request.user
        )
        serializer.save(project=project)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)