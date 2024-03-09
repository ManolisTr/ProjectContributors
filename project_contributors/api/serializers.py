# api/serializers.py
from rest_framework import serializers
from api.models import OpenSourceProject, ExpressionOfInterest, User, ProgrammingSkill


class OpenSourceProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenSourceProject
        fields = ['project_name', 'description',
                  'maximum_collaborators', 'collaborators']

class UserDetailSerializer(serializers.ModelSerializer):
    programming_skills = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'programming_skills']

    def get_programming_skills(self, obj):
        return list(obj.programming_skills.values_list('name', flat=True))

class ExpressionOfInterestSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(source='user', read_only=True)

    class Meta:
        model = ExpressionOfInterest
        fields = ['id', 'user_details', 'status', 'created_at']