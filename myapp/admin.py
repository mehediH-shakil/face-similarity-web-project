from django.contrib import admin
from .models import LostPerson, FindPerson, UserProfile

admin.site.register(LostPerson)
admin.site.register(FindPerson)
admin.site.register(UserProfile)
