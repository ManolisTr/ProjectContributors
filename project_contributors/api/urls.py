from django.urls import path
from api import views

urlpatterns = [
    path('create_user/', views.create_user, name='create_user'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('add_skill/', views.add_skill, name='add_skill'),
    path('remove_skill/', views.remove_skill, name='remove_skill'),
    path('create_project/', views.create_project, name='create_project'),
    path('available_projects/', views.available_projects, name='available_projects'),
    path('projects/<int:project_id>/express_interest/', views.express_interest, name='express_interest'),
    path('projects/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('projects/<int:project_id>/interests/', views.project_interests, name='project_interests'),
    path('projects/<int:project_id>/accept_or_reject_interest/<int:eoi_id>/', views.accept_or_reject_interest, name='accept_or_reject_interest'),



]
