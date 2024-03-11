from django.contrib import admin


# Register your models here.

from api.models import User, ProgrammingSkill, OpenSourceProject, ExpressionOfInterest

admin.site.register(User)
admin.site.register(ProgrammingSkill)
admin.site.register(OpenSourceProject)
admin.site.register(ExpressionOfInterest)

