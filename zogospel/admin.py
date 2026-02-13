from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Musique, Actualite, Magazine, Agenda, Contact

admin.site.register(Musique)
admin.site.register(Actualite)
admin.site.register(Magazine)
admin.site.register(Agenda)
admin.site.register(Contact)
