from rest_framework import serializers
from api.models import OpenSourceProject, ExpressionOfInterest, User, ProgrammingSkill


class OpenSourceProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the OpenSourceProject model.

    This serializer is used to convert OpenSourceProject model instances
    into JSON representations.
    """

    class Meta:
        model = OpenSourceProject
        fields = ['project_name', 'description',
                  'maximum_collaborators', 'collaborators']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the detailed representation of a User model.

    This serializer is used to provide detailed information about a user,
    including their username, email, and programming skills.
    """
    programming_skills = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'programming_skills']

    def get_programming_skills(self, obj):
        return list(obj.programming_skills.values_list('name', flat=True))


class ExpressionOfInterestSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExpressionOfInterest model.

    This serializer is used to represent an ExpressionOfInterest instance,
    including details about the user expressing interest, such as username,
    email, and programming skills.
    """
    user_details = UserDetailSerializer(source='user', read_only=True)

    class Meta:
        model = ExpressionOfInterest
        fields = ['id', 'user_details', 'status', 'created_at']
