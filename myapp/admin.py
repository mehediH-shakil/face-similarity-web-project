from django.contrib import admin
from .models import LostPerson, FindPerson

admin.site.register(LostPerson)
admin.site.register(FindPerson)
