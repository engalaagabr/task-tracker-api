from django.urls import path
# from rest_framework import routers
from rest_framework_nested import routers
from .views import ProjectViewSet, TaskViewSet, RegisterView
from django.conf.urls import include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
    # POST username & password -> returns { access, refresh }
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # POST refresh token -> returns { access }
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
]
