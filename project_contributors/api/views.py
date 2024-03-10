from django.contrib.auth import get_user_model
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ProgrammingSkill
from django.db.models import Count
from django.db.models import F
from api.models import OpenSourceProject, ExpressionOfInterest
from api.serializers import OpenSourceProjectSerializer, ExpressionOfInterestSerializer
from api.utils import check_object_exists
import logging


logger = logging.getLogger(__name__)
MAX_PROGRAMMING_SKILLS = 3  # Maximum number of programming skills a user can have

User = get_user_model()


@api_view(['POST'])
def create_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    # Log incoming request data
    logger.info(f"Received request data: username={username}, email={email}")

    # Check if all required fields are provided
    if not (username and password and email):
        logger.error("Please provide username, password, and email")
        return Response({'error': 'Please provide username, password, and email'}, status=status.HTTP_400_BAD_REQUEST)

    # Log when checking for existing users
    existing_user = check_object_exists(User, username=username)
    if existing_user:
        logger.warning(f"Username '{username}' already exists")
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    existing_email = check_object_exists(User, email=email)
    if existing_email:
        logger.warning(f"Email '{email}' already exists")
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Log when creating a new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        age=request.data.get('age'),
        country=request.data.get('country'),
        residence=request.data.get('residence')
    )
    logger.info(f"User '{username}' created successfully")

    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def reset_password(request):
    if request.method == 'POST':
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if not username or not password:
            logger.error('Username and password are required')
            return Response({'message': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists
        user = check_object_exists(User, username=username)
        if not user:
            logger.error('User does not exist')
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Reset the user's password
        user.set_password(password)
        user.save()

        logger.info(f'Password reset for user: {username}')
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
    else:
        logger.error('Method not allowed')
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_skill(request):
    if request.method == 'POST':
        skill_name = request.data.get('skill_name')

        if not skill_name:
            logger.error('Skill name is required')
            return Response({'message': 'Skill name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already has three skills
        if request.user.programming_skills.count() >= MAX_PROGRAMMING_SKILLS:
            logger.error('Maximum three skills allowed')
            return Response({'message': 'Maximum three skills allowed'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the skill already exists for the user
        if request.user.programming_skills.filter(name=skill_name).exists():
            logger.error(f'Skill "{skill_name}" already exists for the user')
            return Response({'message': f'Skill "{skill_name}" already exists for the user'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the skill already exists in the database
        skill = check_object_exists(ProgrammingSkill, name=skill_name)
        if not skill:
            # Create the skill if it doesn't exist
            skill = ProgrammingSkill.objects.create(name=skill_name)

        # Add the skill to the user's programming_skills
        request.user.programming_skills.add(skill)

        logger.info(f'Skill "{skill_name}" added successfully')
        return Response({'message': 'Skill added successfully'}, status=status.HTTP_201_CREATED)
    else:
        logger.error('Method not allowed')
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def remove_skill(request):
    if request.method == 'POST':
        skill_name = request.data.get('skill_name')

        if not skill_name:
            logger.error('Skill name is required')
            return Response({'message': 'Skill name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the skill exists
        skill = check_object_exists(ProgrammingSkill, name=skill_name)
        if not skill:
            logger.error(f'Skill "{skill_name}" does not exist')
            return Response({'message': f'Skill "{skill_name}" does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has the skill
        if skill not in request.user.programming_skills.all():
            logger.error(f'User does not have skill "{skill_name}"')
            return Response({'message': f'User does not have skill "{skill_name}"'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the skill from the user's programming_skills
        request.user.programming_skills.remove(skill)

        logger.info(f'Skill "{skill_name}" removed successfully')
        return Response({'message': 'Skill removed successfully'}, status=status.HTTP_200_OK)
    else:
        logger.error('Method not allowed')
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def create_project(request):
    if request.method == 'POST':
        serializer = OpenSourceProjectSerializer(data=request.data)
        if serializer.is_valid():
            # Set the creator of the project as the current authenticated user
            serializer.validated_data['creator'] = request.user

            # Check if a project with the same name already exists
            project_name = serializer.validated_data['project_name']
            if check_object_exists(OpenSourceProject, project_name=project_name):
                logger.error('A project with the same name already exists')
                return Response({'message': 'A project with the same name already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the project
            serializer.save()
            logger.info('Project created successfully')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error('Invalid data provided for project creation')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error('Method not allowed')
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def available_projects(request):
    try:
        # Annotate the queryset to count the number of collaborators
        available_projects = OpenSourceProject.objects.annotate(
            num_collaborators=Count('collaborators'))

        # Filter projects with available seats
        available_projects = available_projects.filter(
            num_collaborators__lt=F('maximum_collaborators'))

        # Serialize the projects data
        serialized_projects = []

        for project in available_projects:
            serialized_projects.append({
                'id': project.id,
                'project_name': project.project_name,
                'description': project.description,
                'maximum_collaborators': project.maximum_collaborators,
                'current_collaborators': project.collaborators.count(),
                'creator': project.creator.username,
                'status': project.status
            })

        logger.info('Retrieved available projects successfully')
        return Response(serialized_projects, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Failed to retrieve available projects: {e}')
        return Response({'message': 'Failed to retrieve available projects'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def express_interest(request, project_id):
    try:
        # Check if the project exists
        project = check_object_exists(OpenSourceProject, id=project_id)
        if not project:
            logger.error('Project does not exist')
            return Response({'message': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already expressed interest
        if ExpressionOfInterest.objects.filter(project=project, user=request.user).exists():
            logger.warning(
                'User has already expressed interest in this project')
            return Response({'message': 'User has already expressed interest in this project'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create an expression of interest record for the user and project
        ExpressionOfInterest.objects.create(project=project, user=request.user)

        logger.info('User expressed interest in the project successfully')
        return Response({'message': 'User expressed interest in the project successfully'},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f'Failed to express interest in the project: {e}')
        return Response({'message': 'Failed to express interest in the project'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def close_project(request, project_id):
    # Check if the project exists
    project = check_object_exists(OpenSourceProject, pk=project_id)
    if not project:
        logger.error(f"Project with ID {project_id} does not exist")
        return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the authenticated user is the creator of the project
    if request.user != project.creator:
        logger.error(
            f"User {request.user.username} is not authorized to close project {project_id}")
        return Response({'message': 'Only the creator of the project can close it'}, status=status.HTTP_403_FORBIDDEN)

    # Update the project status to 'closed'
    project.status = 'closed'
    project.save()

    logger.info(f"Project {project_id} closed by user {request.user.username}")
    return Response({'message': 'Project closed successfully'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_project(request, pk):
    try:
        # Check if the project exists
        project = check_object_exists(OpenSourceProject, pk=pk)
        if not project:
            logger.error('Project not found')
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the current user is the creator of the project
        if request.user == project.creator:
            project.delete()
            logger.info('Project deleted successfully')
            return Response({'message': 'Project deleted successfully'}, status=status.HTTP_200_OK)
        else:
            logger.warning('User is not authorized to delete this project')
            return Response({'message': 'You are not authorized to delete this project'}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f'Failed to delete the project: {e}')
        return Response({'message': 'Failed to delete the project'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def project_interests(request, project_id):
    try:
        project = OpenSourceProject.objects.get(id=project_id)
    except OpenSourceProject.DoesNotExist:
        logger.error('Project does not exist')
        return Response({'message': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user is the creator of the project
    if request.user != project.creator:
        logger.warning(
            'User is not authorized to see interests for this project')
        return Response({'message': 'You are not authorized to see interests for this project'}, status=status.HTTP_403_FORBIDDEN)

    interests = ExpressionOfInterest.objects.filter(project=project)
    serializer = ExpressionOfInterestSerializer(interests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def accept_or_reject_interest(request, project_id, eoi_id):
    try:
        eoi = ExpressionOfInterest.objects.get(
            id=eoi_id, project_id=project_id)
    except ExpressionOfInterest.DoesNotExist:
        logger.error('Expression of interest not found')
        return Response({'message': 'Expression of interest not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the authenticated user is the creator of the project
    if request.user != eoi.project.creator:
        logger.warning(
            'Only the creator of the project can accept or reject interests')
        return Response({'message': 'Only the creator of the project can accept or reject interests'}, status=status.HTTP_403_FORBIDDEN)

    # Check if the user is already accepted
    if eoi.status == 'accepted':
        logger.warning('User is already accepted for this project')
        return Response({'message': 'User is already accepted for this project'}, status=status.HTTP_400_BAD_REQUEST)

    # Process the accept/reject action based on the request data
    action = request.data.get('action')
    if action not in ['accept', 'reject']:
        logger.error('Invalid action')
        return Response({'message': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    if action == 'accept':
        # Check if the project has available capacity
        if eoi.project.current_collaborators >= eoi.project.maximum_collaborators:
            logger.warning('Project is already full')
            return Response({'message': 'Project is already full'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the status of the expression of interest to "accepted"
        eoi.status = 'accepted'
        eoi.save()

        # Add the user to the project collaborators
        eoi.project.collaborators.add(eoi.user)

        # Increase the current collaborators count
        eoi.project.current_collaborators += 1
        eoi.project.save()

        # Update the project status to "active" if it's the first user signing up
        if eoi.project.current_collaborators == 1:
            eoi.project.status = 'active'
            eoi.project.save()

        logger.info('Interest accepted successfully')
        return Response({'message': 'Interest accepted successfully'}, status=status.HTTP_200_OK)
    else:
        # Update the status of the expression of interest to "rejected"
        eoi.status = 'rejected'
        eoi.save()

        # Remove the user from the project collaborators
        eoi.project.collaborators.remove(eoi.user)

        # Decrease the current collaborators count

        eoi.project.save()

        logger.info('Interest rejected successfully')
        return Response({'message': 'Interest rejected successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_analytics(request, user_id):
    try:
        user = request.user
        user_projects = user.created_projects.all()
        user_interests = ExpressionOfInterest.objects.filter(user=user)
        user_skills = user.programming_skills.all()

        serialized_data = {
            'user_projects_as_creator': user_projects.count(),
            'projects_name': list(user_projects.values_list('project_name', flat=True)),
            'user_collaborations': user.projects_contributed.count(),
            'collaborations_name': list(user.projects_contributed.values_list('project_name', flat=True)),
            'user_interests': user_interests.count(),
            'interests_project_name': list(user_interests.values_list('project__project_name', flat=True)),
            'user_skills': list(user_skills.values_list('name', flat=True))
        }

        logger.info('User analytics retrieved successfully')
        return Response(serialized_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error retrieving user analytics: {str(e)}')
        return Response({'message': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
