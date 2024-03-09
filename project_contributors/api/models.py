# api/models.py
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Add any additional fields you need
    age = models.IntegerField(null=True)
    country = models.CharField(max_length=100, null=True)
    residence = models.CharField(max_length=100, null=True)
    programming_skills = models.ManyToManyField(
        'ProgrammingSkill', related_name='users', blank=True)

    def __str__(self):
        return self.username


class ProgrammingSkill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OpenSourceProject(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    project_name = models.CharField(max_length=100)
    description = models.TextField()
    maximum_collaborators = models.PositiveIntegerField()
    # This field will be updated when a user joins or leaves a project
    current_collaborators = models.PositiveIntegerField(default=0)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_projects')
    collaborators = models.ManyToManyField(
        User, related_name='projects_contributed', blank=True)

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.project_name


class ExpressionOfInterest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(OpenSourceProject, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.project.project_name} - {self.status}"