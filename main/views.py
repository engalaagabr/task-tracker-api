from django.shortcuts import render
from rest_framework import viewsets
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):  
        return Task.objects.filter(project_id = self.kwargs['project_pk'])

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])