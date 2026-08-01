from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project, Task


class TaskTrackerAPITests(APITestCase):

    def setUp(self):
        # 1. Create primary test user (Password >= 6 characters)
        self.user = User.objects.create_user(
            username='alaa',
            email='alaa@example.com',
            password='Password123!'
        )

        # 2. Create secondary test user for isolation tests
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='Password123!'
        )

        # 3. Pre-create primary user's project
        self.user_project = Project.objects.create(
            name="Alaa's Project",
            description="Owned by primary user",
            owner=self.user
        )

        # 4. Pre-create secondary user's project
        self.other_user_project = Project.objects.create(
            name="Other User's Project",
            description="Owned by secondary user",
            owner=self.other_user
        )

        # Timezone-aware date for Task models
        due_date = timezone.now() + timezone.timedelta(days=7)

        # 5. Pre-create primary user's task
        self.user_task = Task.objects.create(
            title="User Task",
            description="Task in Alaa's project",
            status="TODO",
            priority="HIGH",
            due_date=due_date,
            project=self.user_project
        )

        # 6. Pre-create secondary user's task
        self.other_task = Task.objects.create(
            title="Other Task",
            description="Task in Other's project",
            status="TODO",
            priority="LOW",
            due_date=due_date,
            project=self.other_user_project
        )

        # Setup Endpoints & URLs
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.projects_url = '/api/projects/'
        self.user_project_detail_url = f'/api/projects/{self.user_project.id}/'
        self.other_project_detail_url = f'/api/projects/{self.other_user_project.id}/'

        self.user_tasks_url = f'/api/projects/{self.user_project.id}/tasks/'
        self.user_task_detail_url = f'/api/projects/{self.user_project.id}/tasks/{self.user_task.id}/'
        self.other_tasks_url = f'/api/projects/{self.other_user_project.id}/tasks/'
        self.other_task_detail_url = f'/api/projects/{self.other_user_project.id}/tasks/{self.other_task.id}/'

    # =========================================================================
    # 🔑 AUTHENTICATION TESTS
    # =========================================================================

    def test_register_works(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!"  # Meets min_length >= 6 constraint
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_works(self):
        payload = {
            "username": "alaa",
            "password": "Password123!"
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # =========================================================================
    # 📁 PROJECT TESTS
    # =========================================================================

    def test_authenticated_user_can_create_project(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Brand New Project",
            "description": "Created via API Test"
        }
        response = self.client.post(self.projects_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Brand New Project")

    def test_owner_is_assigned_automatically(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Auto Owner Test",
            "description": "Owner assignment check"
        }
        response = self.client.post(self.projects_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_project = Project.objects.get(id=response.data['id'])
        self.assertEqual(created_project.owner, self.user)

    def test_user_sees_only_their_projects(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.user_project.id)

    def test_cannot_retrieve_another_users_project(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.other_project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_update_works(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Updated Project Name"
        }
        # Using PATCH for partial update to avoid missing required fields errors
        response = self.client.patch(self.user_project_detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user_project.refresh_from_db()
        self.assertEqual(self.user_project.name, "Updated Project Name")

    def test_project_delete_works(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.user_project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.user_project.id).exists())

    # =========================================================================
    # 📌 TASK TESTS & SCOPE ISOLATION
    # =========================================================================

    def test_create_task_inside_owned_project(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "New Task",
            "description": "Task creation test",
            "status": "TODO",
            "priority": "MEDIUM",
            "due_date": "2026-12-31T12:00:00Z"
        }
        response = self.client.post(self.user_tasks_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "New Task")

    def test_list_project_tasks(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.user_tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.user_task.id)

    def test_cannot_access_task_from_another_project(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.other_task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_access_another_users_tasks(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.other_tasks_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_task_update_works(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Updated Task Title",
            "status": "IN_PROGRESS"
        }
        # Using PATCH for partial updates
        response = self.client.patch(self.user_task_detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user_task.refresh_from_db()
        self.assertEqual(self.user_task.title, "Updated Task Title")
        self.assertEqual(self.user_task.status, "IN_PROGRESS")

    def test_task_delete_works(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.user_task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.user_task.id).exists())

    # =========================================================================
    # ⚠️ VALIDATION TESTS
    # =========================================================================

    def test_invalid_status_returns_400(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Invalid Status Task",
            "status": "INVALID_STATUS_VALUE",
            "priority": "HIGH"
        }
        response = self.client.post(self.user_tasks_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_invalid_priority_returns_400(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Invalid Priority Task",
            "status": "TODO",
            "priority": "INVALID_PRIORITY"
        }
        response = self.client.post(self.user_tasks_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('priority', response.data)

    def test_blank_title_returns_400(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "",
            "status": "TODO",
            "priority": "MEDIUM"
        }
        response = self.client.post(self.user_tasks_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_invalid_due_date_returns_400(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Invalid Date Task",
            "status": "TODO",
            "priority": "MEDIUM",
            "due_date": "invalid-datetime-string"
        }
        response = self.client.post(self.user_tasks_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('due_date', response.data)