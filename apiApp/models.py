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

class user_address(models.Model):
    user_id = models.TextField()
    add_line_1 = models.TextField()
    add_line_2 = models.TextField(null=True,blank=True)
    landmark = models.TextField(null=True,blank=True)
    city = models.TextField()
    state = models.TextField()
    country = models.TextField()
    pincode = models.TextField()
    phone_no = models.TextField()

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


class user_whishlist(models.Model):
    product_id = models.TextField()
    user_id = models.TextField()
    

class user_cart(models.Model):
    user_id = models.TextField()
    product_id = models.TextField()
    size = models.TextField()
    diamond_quality = models.TextField()
    quantity = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
