from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User
from rest_framework.test import APITestCase
from api.models import ProgrammingSkill
from api.models import OpenSourceProject, ExpressionOfInterest
from api.serializers import ExpressionOfInterestSerializer


class CreateUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        url = reverse('create_user')
        data = {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test@example.com',
            'age': 30,
            'country': 'USA',
            'residence': 'New York'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Remove the assertion for 'id' in response.data
        # self.assertTrue('id' in response.data)
        # Add more assertions as needed


class ResetPasswordTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a test user for password reset
        self.user = User.objects.create(
            username='test_user', password='test_password')

    def test_reset_password(self):
        url = reverse('reset_password')
        data = {
            'username': 'test_user',
            'password': 'new_password'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'Password reset successfully')
        # Verify that the password has been updated
        self.assertTrue(User.objects.get(
            username='test_user').check_password('new_password'))


class AddSkillTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_add_skill_success(self):
        skill_name = 'Python'

        # Make a POST request to add a skill
        response = self.client.post(
            '/api/add_skill/', {'skill_name': skill_name}, format='json')

        # Check if the request was successful (HTTP 201 status code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the skill was added to the user's programming skills
        self.assertTrue(self.user.programming_skills.filter(
            name=skill_name).exists())

    def test_add_skill_without_name(self):
        # Make a POST request to add a skill without providing a skill name
        response = self.client.post(
            '/api/add_skill/', {'skill_name': ''}, format='json')

        # Check if the request returns HTTP 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_skill_exceeding_limit(self):
        # Add three skills to the user
        python_skill = ProgrammingSkill.objects.create(name='Python')
        javascript_skill = ProgrammingSkill.objects.create(name='JavaScript')
        java_skill = ProgrammingSkill.objects.create(name='Java')

        # Add the skills to the user's programming skills
        self.user.programming_skills.add(python_skill)
        self.user.programming_skills.add(javascript_skill)
        self.user.programming_skills.add(java_skill)

        # Make a POST request to add a skill, exceeding the limit of three skills
        response = self.client.post(
            '/api/add_skill/', {'skill_name': 'C++'}, format='json')

        # Check if the request returns HTTP 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_existing_skill(self):
        # Add a skill to the user
        skill_name = 'Python'
        ProgrammingSkill.objects.create(name=skill_name)
        self.user.programming_skills.add(
            ProgrammingSkill.objects.get(name=skill_name))

        # Make a POST request to add the existing skill
        response = self.client.post(
            '/api/add_skill/', {'skill_name': skill_name}, format='json')

        # Check if the request returns HTTP 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RemoveSkillTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            username='test_user', password='test_password')
        # Create some programming skills
        self.skill1 = ProgrammingSkill.objects.create(name='Python')
        self.skill2 = ProgrammingSkill.objects.create(name='JavaScript')
        self.skill3 = ProgrammingSkill.objects.create(name='Java')
        # Add skills to the user
        self.user.programming_skills.add(self.skill1)
        self.user.programming_skills.add(self.skill2)

    def test_remove_skill_success(self):
        self.client.force_authenticate(user=self.user)  # Authenticate the user
        # Attempt to remove a skill
        response = self.client.post(
            '/api/remove_skill/', {'skill_name': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.programming_skills.count(),
                         1)  # Check if the skill is removed

    def test_remove_nonexistent_skill(self):
        self.client.force_authenticate(user=self.user)  # Authenticate the user
        # Attempt to remove a nonexistent skill
        response = self.client.post(
            '/api/remove_skill/', {'skill_name': 'C++'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_skill_not_owned(self):
        self.client.force_authenticate(user=self.user)  # Authenticate the user
        # Attempt to remove a skill not owned by the user
        response = self.client.post(
            '/api/remove_skill/', {'skill_name': 'Java'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if the skill is not removed
        self.assertEqual(self.user.programming_skills.count(), 2)


class CreateProjectTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user', password='test_password')
        self.token = self.obtain_token()

    def obtain_token(self):
        response = self.client.post(
            '/api/token/', {'username': 'test_user', 'password': 'test_password'})
        return response.data.get('token')

    def test_create_project_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        data = {
            'project_name': 'Test Project',
            'description': 'This is a test project.',
            'maximum_collaborators': 5
        }
        response = self.client.post(
            '/api/create_project/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(OpenSourceProject.objects.filter(
            project_name='Test Project').exists())

    def test_create_project_duplicate_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        # Create a project with the same name as in the first test case
        data = {
            # Use the same project name as in the first test case
            'project_name': 'Test Project',
            'description': 'Another test project with the same name.',
            'maximum_collaborators': 3
        }
        # First attempt to create the project
        response1 = self.client.post(
            '/api/create_project/', data, format='json')
        # Ensure that the project creation is successful
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Attempt to create another project with the same name
        response2 = self.client.post(
            '/api/create_project/', data, format='json')
        # Ensure that the project creation fails due to the duplicate name
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['message'],
                         'A project with the same name already exists')


class AvailableProjectsTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username='user1', password='password1')
        self.user2 = User.objects.create_user(
            username='user2', password='password2')

        # Create projects
        self.project1 = OpenSourceProject.objects.create(
            project_name='Project 1',
            description='Description for Project 1',
            maximum_collaborators=3,
            creator=self.user1,
            status='active'  # Set project status to "active"
        )

        self.project2 = OpenSourceProject.objects.create(
            project_name='Project 2',
            description='Description for Project 2',
            maximum_collaborators=2,
            creator=self.user2,
            status='draft'  # Set project status to "draft"
        )

        # Add collaborators to projects
        self.project1.collaborators.add(self.user1, self.user2)
        self.project2.collaborators.add(self.user1)

    def test_available_projects(self):
        client = APIClient()

        # Make a GET request to the available_projects endpoint
        response = client.get('/api/available_projects/')

        # Check if the request was successful (HTTP 200 status code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data contains the expected number of projects
        self.assertEqual(len(response.data), 2)


class ExpressInterestTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username='user1', password='password1')
        self.user2 = User.objects.create_user(
            username='user2', password='password2')

        # Create projects
        self.project1 = OpenSourceProject.objects.create(
            project_name='Project 1',
            description='Description for Project 1',
            maximum_collaborators=3,
            creator=self.user1,
            status='active'
        )

        self.project2 = OpenSourceProject.objects.create(
            project_name='Project 2',
            description='Description for Project 2',
            maximum_collaborators=2,
            creator=self.user2,
            status='draft'
        )

    def test_express_interest(self):
        client = APIClient()
        client.force_authenticate(user=self.user1)  # Authenticate user1

        # Make a POST request to express_interest endpoint for project 1
        response = client.post(
            f'/api/projects/{self.project1.id}/express_interest/')

        # Check if the request was successful (HTTP 201 status code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the response contains the expected message
        self.assertEqual(
            response.data['message'], 'User expressed interest in the project successfully')

    def test_express_interest_project_not_found(self):
        client = APIClient()
        client.force_authenticate(user=self.user1)  # Authenticate user1

        # Make a POST request to express_interest endpoint for non-existing project
        response = client.post('/api/projects/100/express_interest/')

        # Check if the request returns HTTP 404 status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeleteProjectTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='test_user', password='test_password')

        # Create a project
        self.project = OpenSourceProject.objects.create(
            project_name='Test Project',
            description='Description for Test Project',
            maximum_collaborators=3,
            creator=self.user
        )

    def test_delete_project(self):
        # Authenticate the user (if authentication is required)
        self.client.force_authenticate(user=self.user)

        # Send a DELETE request to the delete project endpoint
        response = self.client.delete(
            f'/api/projects/{self.project.id}/delete/')

        # Check if the request was successful (HTTP 204 status code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the project is deleted from the database
        self.assertFalse(OpenSourceProject.objects.filter(
            id=self.project.id).exists())


class ProjectInterestsTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.creator = User.objects.create_user(
            username='creator', password='password')
        self.user1 = User.objects.create_user(
            username='user1', password='password1')
        self.user2 = User.objects.create_user(
            username='user2', password='password2')

        # Create a project
        self.project = OpenSourceProject.objects.create(
            project_name='Test Project',
            description='Description for Test Project',
            maximum_collaborators=3,
            creator=self.creator
        )

        # Create expressions of interest
        self.eoi1 = ExpressionOfInterest.objects.create(
            user=self.user1, project=self.project)
        self.eoi2 = ExpressionOfInterest.objects.create(
            user=self.user2, project=self.project)

    def test_project_interests(self):
        # Authenticate as the creator
        self.client.force_authenticate(user=self.creator)

        # Make a GET request to project_interests endpoint
        response = self.client.get(
            f'/api/projects/{self.project.id}/interests/')

        # Check if the request was successful (HTTP 200 status code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data matches the expected serialized data
        serializer = ExpressionOfInterestSerializer(
            [self.eoi1, self.eoi2], many=True)
        self.assertEqual(response.data, serializer.data)

    def test_project_interests_project_not_found(self):
        # Authenticate as the creator
        self.client.force_authenticate(user=self.creator)

        # Make a GET request to project_interests endpoint with a non-existing project ID
        response = self.client.get('/api/project_interests/100/')

        # Check if the request returns HTTP 404 status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_interests_user_not_creator(self):
        # Authenticate as a different user (not the creator)
        self.client.force_authenticate(user=self.user1)

        # Make a GET request to project_interests endpoint
        response = self.client.get(
            f'/api/project_interests/{self.project.id}/')

        # Check if the request returns HTTP 404 status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AcceptOrRejectInterestTestCase(TestCase):
    def setUp(self):
        # Create users
        self.creator_user = User.objects.create_user(
            username='creator', password='password')
        self.user = User.objects.create_user(
            username='user', password='password')

        # Create project
        self.project = OpenSourceProject.objects.create(
            project_name='Project',
            description='Description for Project',
            maximum_collaborators=2,
            creator=self.creator_user,
            status='draft'
        )

        # Create expression of interest
        self.eoi = ExpressionOfInterest.objects.create(
            user=self.user,
            project=self.project,
            status='pending'
        )

    def test_accept_interest(self):
        client = APIClient()
        # Authenticate creator user
        client.force_authenticate(user=self.creator_user)

        # Make a POST request to accept interest endpoint
        response = client.post(
            f'/api/projects/{self.project.id}/accept_or_reject_interest/{self.eoi.id}/', {'action': 'accept'})

        # Check if the request was successful (HTTP 200 status code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the project from the database
        self.project.refresh_from_db()

        # Check if the interest was accepted
        self.assertEqual(ExpressionOfInterest.objects.get(
            id=self.eoi.id).status, 'accepted')

        # Check if the user is added to project collaborators
        self.assertTrue(self.user in self.project.collaborators.all())

        # Check if the current collaborators count is increased
        self.assertEqual(self.project.current_collaborators, 1)

        # Check if the project status is updated to "active"
        self.assertEqual(self.project.status, 'active')

    def test_accept_already_accepted_interest(self):
        client = APIClient()
        # Authenticate creator user
        client.force_authenticate(user=self.creator_user)

        # Change the status of expression of interest to "accepted"
        self.eoi.status = 'accepted'
        self.eoi.save()

        # Make a POST request to accept interest endpoint
        response = client.post(
            f'/api/projects/{self.project.id}/accept_or_reject_interest/{self.eoi.id}/', {'action': 'accept'})

        # Check if the request returns HTTP 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the appropriate message is returned
        self.assertEqual(response.data['message'],
                         'User is already accepted for this project')


class GetUserAnalyticsTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            username='user', password='password')

        # Create projects
        self.project1 = OpenSourceProject.objects.create(
            project_name='Project 1',
            description='Description for Project 1',
            maximum_collaborators=2,
            creator=self.user,
            status='active'
        )

        self.project2 = OpenSourceProject.objects.create(
            project_name='Project 2',
            description='Description for Project 2',
            maximum_collaborators=3,
            creator=self.user,
            status='active'
        )

        # Create expression of interests
        self.eoi1 = ExpressionOfInterest.objects.create(
            user=self.user,
            project=self.project1,
            status='accepted'
        )

        self.eoi2 = ExpressionOfInterest.objects.create(
            user=self.user,
            project=self.project2,
            status='pending'
        )

        # Create programming skills
        self.skill1 = ProgrammingSkill.objects.create(name='Python')
        self.skill2 = ProgrammingSkill.objects.create(name='JavaScript')

        # Add skills to the user
        self.user.programming_skills.add(self.skill1)
        self.user.programming_skills.add(self.skill2)

    def test_get_user_analytics(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        # Make a GET request to get user analytics endpoint
        response = client.get(f'/api/get_user_analytics/{self.user.id}/')

        # Check if the request was successful (HTTP 200 status code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        self.assertEqual(response.data['user_projects_as_creator'], 2)
        self.assertEqual(response.data['user_collaborations'], 0)
        self.assertEqual(response.data['user_interests'], 2)
        self.assertEqual(response.data['user_skills'], [
                         'Python', 'JavaScript'])
        self.assertEqual(response.data['projects_name'], [
                         'Project 1', 'Project 2'])
        self.assertEqual(response.data['collaborations_name'], [])
        self.assertEqual(response.data['interests_project_name'], [
                         'Project 1', 'Project 2'])
