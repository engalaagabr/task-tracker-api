from django.urls import path
# from rest_framework import routers
from rest_framework_nested import routers
from .views import ProjectViewSet, TaskViewSet
from django.conf.urls import include

router = routers.SimpleRouter()

router.register('projects', ProjectViewSet, basename = 'project')

projects_router = routers.NestedSimpleRouter(
    router,
    'projects',
    lookup = 'project'
    
)

projects_router.register(
    'tasks',
    TaskViewSet,
    basename = 'task'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
]
