from django.contrib import admin
from .models import MainMembers, Dependents, Treasury, TreasuryDep

admin.site.register(MainMembers)
admin.site.register(Dependents)
admin.site.register(Treasury)
admin.site.register(TreasuryDep)

# Register your models here.
