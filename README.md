# Project Contributors API

### Table of Contents
- [Project Contributors API](#project-contributors-api)
    - [Table of Contents](#table-of-contents)
    - [About the Project](#about-the-project)
    - [Features](#features)
    - [Technologies Used](#technologies-used)
    - [Python and Django Versions](#python-and-django-versions)
    - [Getting Started](#getting-started)
    - [API Endpoints](#api-endpoints)
  - [Endpoints Summary](#endpoints-summary)
    - [Testing](#testing)
  - [Technical Documentation](#technical-documentation)
      - [Structure](#structure)
      - [Database Schema](#database-schema)
  - [Running the Application](#running-the-application)
    - [Assumptions](#assumptions)
    - [Create User](#create-user)
    - [Reset Password](#reset-password)
    - [Get Token](#get-token)
    - [Add Skill (same for remove skill)](#add-skill-same-for-remove-skill)
    - [Create Project](#create-project)
    - [Available Projects](#available-projects)
    - [Express Interest](#express-interest)
    - [Close Project](#close-project)
    - [Delete Project](#delete-project)
    - [Project Interests](#project-interests)
    - [Accept or Reject Interest](#accept-or-reject-interest)
    - [Get User Analytics](#get-user-analytics)

### About the Project
The Project Contributors API is a platform designed to connect programmers and facilitate collaboration on open-source projects. It provides a RESTful API that allows users to register, manage their skills, create and join projects, and view their overall statistics.

### Features
1. User Registration: Register with basic information such as name, email, age, country, residence, and username.
2. Password Reset: Reset your password if you forget it.
3. Skill Management: Add or remove programming skills, with a maximum limit of three skills.
4. Project Creation: Create new open-source projects with details like project name, description, and maximum collaborators.
5. Project Collaboration: Join open projects and express interest in participating.
6. User Statistics: View overall statistics, including the number of projects contributed and created.

### Technologies Used
- Django: A Python web framework for rapid development and clean design.
- Django REST Framework (DRF): Used to build RESTful APIs quickly and easily.
- SQLite: Lightweight and easy-to-use database backend for development.
- Git and GitHub: Version control and repository hosting for collaboration and code management.

### Python and Django Versions
- Python 3.11
- Django 5.0

### Getting Started

To get started with the Project Contributors API, open your favorite text editor and follow the instructions below.:

1. Create and activate a virtual environment (optional):
   
Linux/MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Clone the repository from GitHub:
```bash
git clone git@github.com:ManolisTr/ProjectContributors.git
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python manage.py runserver
```


### API Endpoints

## Endpoints Summary

- **Create User**
  - URL: `/create_user/`
  - Method: POST
  - Description: Endpoint to register new users with their principal information.

- **Reset Password**
  - URL: `/reset_password/`
  - Method: POST
  - Description: Endpoint to reset the password for existing users.

- **Add Skill**
  - URL: `/add_skill/`
  - Method: POST
  - Description: Endpoint to add a new skill to a user's profile.

- **Remove Skill**
  - URL: `/remove_skill/`
  - Method: POST
  - Description: Endpoint to remove a skill from a user's profile.

- **Create Project**
  - URL: `/create_project/`
  - Method: POST
  - Description: Endpoint for registered users to create new open-source projects.

- **Available Projects**
  - URL: `/available_projects/`
  - Method: GET
  - Description: Endpoint to fetch open-source projects with available seats for collaboration.

- **Express Interest**
  - URL: `/projects/<int:project_id>/express_interest/`
  - Method: POST
  - Description: Endpoint for users to express interest in joining a project.

- **Close Project**
  - URL: `/projects/close/<int:project_id>/`
  - Method: POST
  - Description: Endpoint for the creator of a project to close it.

- **Delete Project**
  - URL: `/projects/<int:pk>/delete/`
  - Method: DELETE
  - Description: Endpoint for the creator of a project to delete it.

- **Project Interests**
  - URL: `/projects/<int:project_id>/interests/`
  - Method: GET
  - Description: Endpoint to fetch interests expressed for a specific project.

- **Accept or Reject Interest**
  - URL: `/projects/<int:project_id>/accept_or_reject_interest/<int:eoi_id>/`
  - Method: POST
  - Description: Endpoint for the creator of a project to accept or reject interest from other users.

- **Get User Analytics**
  - URL: `/get_user_analytics/<int:user_id>/`
  - Method: GET
  - Description: Endpoint to retrieve overall statistics for a specific user.


### Testing
This project includes a comprehensive test suite to ensure the reliability and functionality of the API endpoints. The tests cover various scenarios and edge cases to verify the behavior of the application under different conditions. The testing framework used for this project is Django's built-in testing framework.

To run the tests, execute the following command in your terminal:
```bash
python manage.py test api
```


## Technical Documentation

#### Structure

```bash
project_contributors/
│
├── api/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
│
├── project_contributors/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── manage.py           
│
├── requirements.txt    
│
├── README.md           
│
└── venv/               
```

#### Database Schema

```sql
+-------------------+         +---------------------+        +--------------------------+
|       User        |         |   ProgrammingSkill  |        |    OpenSourceProject     |
+-------------------+         +---------------------+        +--------------------------+
| - id: PK          |         | - id: PK            |        | - id: PK                 |
| - username        | <-----> | - name              | <----> | - project_name           |
| - password        |         +---------------------+        | - description            |
| - email           |                                        | - maximum_collaborators  |
| - age             |                                        | - current_collaborators  |
| - country         |                                        | - creator: FK(User)      |
| - residence       |                                        | - collaborators: M2M(User)|
+-------------------+                                        | - status                 |
                                                              +--------------------------+

+--------------------------+
|    ExpressionOfInterest  |
+--------------------------+
| - id: PK                 |
| - user: FK(User)        |
| - project: FK(OpenSourceProject)|
| - status                 |
| - created_at             |
+--------------------------+
```

## Running the Application

Via postman or any other API client, you can interact with the API endpoints to perform various operations. Below are some examples of how to use the API.

### Assumptions
- Only authenticated users can add skills, create projects, and express interest in projects and view the analytics.
- The maximum number of skills a user can have is three and there is not allowed to have the same skill than once.
- All users can view the available projects and express interest in them.
- The creator of a project can close it, delete it, and accept or reject interest from other users.
- The maximum number of collaborators for a project is determined by the creator.
- Only if the creator accepts the interest, the user is added to the project.


### Create User
- POST: http://localhost:8000/api/create_user/
- Request Body:
```json
{
    "username": "test_user",
    "password": "test_user",
    "email":"test_user@gmail.com"
}
```

### Reset Password
- POST: http://localhost:8000/api/reset_password/
- Request Body:
```json
{
    "username": "test_user",
    "password": "test_user1"
}
```

In order to add skill or to user the rest of the endpoints, you need to login first. You can use the following endpoint to get the token.

### Get Token
- POST: http://localhost:8000/api/token/
- In body in the section of x-www-form-urlencoded add the following:
  - username: test_user
  - password: test_user

### Add Skill (same for remove skill)
- POST: http://localhost:8000/api/add_skill/
- In headers add the following:
  - Authorization: Token <token>
- Body:
```json
{
    "name": "Python"
}
```
### Create Project
- POST: http://localhost:8000/api/create_project/
- In headers add the following:
  - Authorization: Token <token>
- Body:
```json
{
    "project_name": "Project 1",
    "description": "Description of project 1",
    "maximum_collaborators": 5
}
```

### Available Projects
- GET: http://localhost:8000/api/available_projects/

### Express Interest
- POST: http://localhost:8000/api/projects/<int:project_id>/express_interest/
- In headers add the following:
  - Authorization: Token <token>

### Close Project
- POST: http://localhost:8000/api/projects/close/<int:project_id>/
- In headers add the following:
  - Authorization
  
### Delete Project
- DELETE: http://localhost:8000/api/projects/<int:pk>/delete/

### Project Interests
- GET: http://localhost:8000/api/projects/<int:project_id>/interests/
  
### Accept or Reject Interest
- POST: http://localhost:8000/api/projects/<int:project_id>/accept_or_reject_interest/<int:eoi_id>/
- In headers add the following:
  - Authorization
- Body:
```json
{
    "status": "accepted"
}
```

### Get User Analytics
- GET: http://localhost:8000/api/get_user_analytics/<int:user_id>/
- In headers add the following:
  - Authorization

