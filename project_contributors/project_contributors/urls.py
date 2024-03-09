# api/urls.py

# from django.urls import path
# from api import views

# urlpatterns = [
#     path('create_user/', views.create_user, name='create_user'),
#     path('reset_password/', views.reset_password, name='reset_password'),
#     path('add_skill/', views.add_skill, name='add_skill'),
#     path('add_skill/', views.remove_skill, name='remove_skill'),
# ]

# from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),  # Include the API URLs
]