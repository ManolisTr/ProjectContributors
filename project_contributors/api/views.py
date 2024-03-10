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


User = get_user_model()


@api_view(['POST'])
def create_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    # Check if all required fields are provided
    if not (username and password and email):
        return Response({'error': 'Please provide username, password, and email'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the username already exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the user using Django's ORM
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        age=request.data.get('age'),
        country=request.data.get('country'),
        residence=request.data.get('residence')
    )

    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def reset_password(request):
    if request.method == 'POST':
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if not username or not password:
            return Response({'message': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(password)
        user.save()

        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_skill(request):
    if request.method == 'POST':
        skill_name = request.data.get('skill_name')

        if not skill_name:
            return Response({'message': 'Skill name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already has three skills
        if request.user.programming_skills.count() >= 3:
            return Response({'message': 'Maximum three skills allowed'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the skill already exists for the user
        if request.user.programming_skills.filter(name=skill_name).exists():
            return Response({'message': f'Skill "{skill_name}" already exists for the user'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or get the skill
        skill, created = ProgrammingSkill.objects.get_or_create(
            name=skill_name)

        # Add the skill to the user's programming_skills
        request.user.programming_skills.add(skill)

        return Response({'message': 'Skill added successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def remove_skill(request):
    if request.method == 'POST':
        skill_name = request.data.get('skill_name')

        if not skill_name:
            return Response({'message': 'Skill name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the skill exists
        try:
            skill = ProgrammingSkill.objects.get(name=skill_name)
        except ProgrammingSkill.DoesNotExist:
            return Response({'message': 'Skill does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has the skill
        if skill not in request.user.programming_skills.all():
            return Response({'message': 'User does not have this skill'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the skill from the user's programming_skills
        request.user.programming_skills.remove(skill)

        return Response({'message': 'Skill removed successfully'}, status=status.HTTP_200_OK)
    else:
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
            if OpenSourceProject.objects.filter(project_name=project_name).exists():
                return Response({'message': 'A project with the same name already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the project
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def available_projects(request):
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

    return Response(serialized_projects, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def express_interest(request, project_id):
    try:
        project = OpenSourceProject.objects.get(id=project_id)
    except OpenSourceProject.DoesNotExist:
        return Response({'message': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has already expressed interest
    if ExpressionOfInterest.objects.filter(project=project, user=request.user).exists():
        return Response({'message': 'User has already expressed interest in this project'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Create an expression of interest record for the user and project
    ExpressionOfInterest.objects.create(project=project, user=request.user)

    return Response({'message': 'User expressed interest in the project successfully'},
                    status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_project(request, pk):
    try:
        project = OpenSourceProject.objects.get(pk=pk)
    except OpenSourceProject.DoesNotExist:
        return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user is the creator of the project
    if request.user == project.creator:
        project.delete()
        return Response({'message': 'Project deleted successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'You are not authorized to delete this project'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def project_interests(request, project_id):
    try:
        project = OpenSourceProject.objects.get(
            id=project_id, creator=request.user)
    except OpenSourceProject.DoesNotExist:
        return Response({'message': 'Project does not exist or You are not authorized to see this project'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response({'message': 'Expression of interest not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the authenticated user is the creator of the project
    if request.user != eoi.project.creator:
        return Response({'message': 'Only the creator of the project can accept or reject interests'}, status=status.HTTP_403_FORBIDDEN)

    # Check if the user is already accepted
    if eoi.status == 'accepted':
        return Response({'message': 'User is already accepted for this project'}, status=status.HTTP_400_BAD_REQUEST)

    # Process the accept/reject action based on the request data
    action = request.data.get('action')
    if action not in ['accept', 'reject']:
        return Response({'message': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    if action == 'accept':
        # Check if the project has available capacity
        if eoi.project.current_collaborators >= eoi.project.maximum_collaborators:
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

        return Response({'message': 'Interest accepted successfully'}, status=status.HTTP_200_OK)
    else:
        # Update the status of the expression of interest to "rejected"
        eoi.status = 'rejected'
        eoi.save()

        # Remove the user from the project collaborators
        eoi.project.collaborators.remove(eoi.user)

        # Decrease the current collaborators count

        eoi.project.save()

        return Response({'message': 'Interest rejected successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_analytics(request, user_id):
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

    return Response(serialized_data, status=status.HTTP_200_OK)
