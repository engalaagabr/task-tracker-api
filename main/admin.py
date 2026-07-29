from django.contrib import admin
from .models import Project, Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')

admin.site.register(Project)
admin.site.register(Task, TaskAdmin)
# Register your models here.
