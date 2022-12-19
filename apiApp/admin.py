from django.contrib import admin

from apiApp.models import product_data
from apiApp.models import user_data

# Register your models here.

admin.site.register(product_data)
admin.site.register(user_data)
