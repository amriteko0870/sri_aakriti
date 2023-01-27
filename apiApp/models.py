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
    name = models.TextField(blank=True)
    category = models.TextField(blank=True)
    image = models.TextField(blank=True)
    gender = models.TextField(blank=True)
    diamond_quality = models.TextField(blank=True)
    diamond_size = models.TextField(blank=True)
    diamond_peice = models.TextField(blank=True)
    diamond_wight = models.TextField(blank=True)
    size = models.TextField(blank=True)
    weight = models.TextField(blank=True)
    actual_price = models.TextField(blank=True)
    selling_price = models.TextField(blank=True)
    discount = models.TextField(blank=True)
    status = models.BooleanField()


class user_whishlist(models.Model):
    product_id = models.TextField()
    user_id = models.TextField()
    

class user_cart(models.Model):
    user_id = models.TextField()
    product_id = models.TextField()
    size = models.TextField()
    weight = models.TextField()
    diamond_quality = models.TextField()
    diamond_size = models.TextField()
    quantity = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)


# ------------------------------- Pricing -----------------------------------------

class diamond_pricing(models.Model):
    diamond_quality = models.TextField()
    diamond_size = models.TextField()
    diamond_pricing = models.TextField()

class metal_price(models.Model):
    platinum = models.TextField()
    gold = models.TextField()
    making_charges = models.TextField()


# -------------------------  Orders ----------------------------------------------------

class order_payment(models.Model):
    user_id = models.TextField()
    order_product = models.CharField(max_length=100)
    order_amount = models.CharField(max_length=25)
    order_payment_id = models.CharField(max_length=100)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)
    order_status = models.TextField(max_length=1,default='p',choices=(('p','p'),('c','c'),('d','d'),('o','o'))) # p placed # d delivered # c canceled # o on the way
    # address_id = m


class order_details(models.Model):
    order_id = models.TextField()
    product_id = models.TextField()
    size = models.TextField()
    weight = models.TextField()
    diamond_quality = models.TextField()
    diamond_size = models.TextField(blank=True)
    quantity = models.TextField()
    platinum = models.TextField()
    gold = models.TextField()
    making_charges = models.TextField()
    diamond = models.TextField()
    shipping = models.TextField()
    tax = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    