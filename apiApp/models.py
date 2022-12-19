from django.db import models

# Create your models here.



class user_data(models.Model):
    name = models.TextField()
    email = models.TextField()
    gender = models.TextField()
    dob = models.TextField()
    phone_code = models.TextField()
    phone_no = models.TextField()
    password = models.TextField()
    token = models.TextField()
    

class product_data(models.Model):
    name = models.TextField()
    category = models.TextField()
    image = models.TextField()
    gender = models.TextField()
    diamond_quality = models.TextField()
    size = models.TextField()
    weight = models.TextField()
    actual_price = models.TextField()
    selling_price = models.TextField()
    discount = models.TextField()
    status = models.TextField()

