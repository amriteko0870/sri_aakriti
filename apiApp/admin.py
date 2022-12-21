from django.contrib import admin

from apiApp.models import product_data
from apiApp.models import user_data,user_address,user_whishlist

# Register your models here.

admin.site.register(product_data)
admin.site.register(user_data)
admin.site.register(user_address)
admin.site.register(user_whishlist)
