# api/models.py
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Additional fields:
        - age: IntegerField for user's age.
        - country: CharField for user's country.
        - residence: CharField for user's residence.
        - programming_skills: Many-to-Many relationship with ProgrammingSkill model.

    Methods:
        - __str__: Returns the username of the user.
    """
    age = models.IntegerField(null=True)
    country = models.CharField(max_length=100, null=True)
    residence = models.CharField(max_length=100, null=True)
    programming_skills = models.ManyToManyField(
        'ProgrammingSkill', related_name='users', blank=True)

    def __str__(self):
        return self.username


class ProgrammingSkill(models.Model):
    """
    Model representing a programming skill.

    Fields:
        - name: CharField representing the name of the programming skill.

    Methods:
        - __str__: Returns the name of the programming skill.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OpenSourceProject(models.Model):
    """
    Model representing an open-source project.

    Fields:
        - project_name: CharField representing the name of the project.
        - description: TextField containing the description of the project.
        - maximum_collaborators: PositiveIntegerField indicating the maximum number of collaborators allowed for the project.
        - current_collaborators: PositiveIntegerField indicating the current number of collaborators for the project.
        - creator: ForeignKey linking to the User model, representing the creator of the project.
        - collaborators: ManyToManyField linking to the User model, representing the collaborators of the project.
        - status: CharField representing the status of the project (draft, active, closed).

    Methods:
        - __str__: Returns the name of the project.
    """
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
    """
    Model representing an expression of interest by a user in an open-source project.

    Fields:
        - user: ForeignKey linking to the User model, representing the user expressing interest.
        - project: ForeignKey linking to the OpenSourceProject model, representing the project of interest.
        - status: CharField representing the status of the expression of interest (pending, accepted, rejected).
        - created_at: DateTimeField indicating the date and time when the expression of interest was created.

    Methods:
        - __str__: Returns a string representation of the expression of interest.
    """
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