import numpy as np
import pandas as pd
import time
from datetime import datetime as dt
import datetime
import re
from operator import itemgetter 
import os
import random
#-------------------------Django Modules---------------------------------------------
from django.http import Http404, HttpResponse, JsonResponse,FileResponse
from django.shortcuts import render
from django.db.models import Avg,Count,Case, When, IntegerField,Sum,FloatField,CharField
from django.db.models import F,Func,Q
from django.db.models import Value as V
from django.db.models.functions import Concat,Cast,Substr
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Min, Max
from django.db.models import Subquery
#----------------------------restAPI--------------------------------------------------
from rest_framework.decorators import parser_classes,api_view
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.response import Response

#----------------------------models---------------------------------------------------
from apiApp.models import user_data,user_address
from apiApp.models import user_whishlist
from apiApp.models import product_data
from apiApp.models import user_cart
from apiApp.models import metal_price,diamond_pricing
from apiApp.models import order_payment
from apiApp.models import order_details


#----------------------------extra---------------------------------------------------

@api_view(['POST'])
def order_view(request,format=None):
    token = request.data['token']
    try:
        user = user_data.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)

    orders = order_payment.objects.filter(user_id = user.id)\
                                  .annotate(
                                            delivery_status = F('order_status'),
                                            date = F('order_date'),
                                            order_price = F('order_amount'),
                                            order_id = F('id')
                                            ).values('delivery_status','date','order_price','order_id')
    
    def deliveryStatus(x):
        if x  == 'd':
            return 'Delivered'
        if x  == 'p':
            return 'Placed'
        if x  == 'c':
            return 'Cancelled'
        if x  == 'o':
            return 'On the way'
    
    def orderDate(x):
        new_date = dt.strptime(str(x)[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        return new_date
    
    if len(orders) > 0:
        df = pd.DataFrame(orders)
        df['delivery_status'] = df['delivery_status'].apply(deliveryStatus)
        df['date'] = df['date'].apply(orderDate)
        order_list = df.to_dict(orient='record')
        res = {
                'status':True,
                'order_list':order_list
              }
    else:
        res = {
                'status':True,
                'order_list':[]
              }
    return Response(res)


@api_view(['POST'])
def orderDetails(request,format=None):
    token = request.data['token']
    order_id = request.data['order_id']

    try:
        user = user_data.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)

    try:
        order = order_payment.objects.get(user_id = user.id,id = order_id)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)

    def deliveryStatus(x):
        if x  == 'd':
            return 'Delivered'
        if x  == 'p':
            return 'Placed'
        if x  == 'c':
            return 'Cancelled'
        if x  == 'o':
            return 'On the way'
    def orderDate(x):
        new_date = dt.strptime(str(x)[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        return new_date

    order_list = order_details.objects.filter(order_id = order_id)
    product_list = product_data.objects.values()
    res = {}
    res['order_date'] = orderDate(order.order_date)
    res['delivery_status'] = deliveryStatus(order.order_status)
    res['order_id'] = order_id
    res['customer_name'] = user.name 
    res['customer_email'] = user.email 
    res['customer_phone'] = user.phone_code + ' ' + user.phone_no 

    products = []
    final_sub_total = 0
    final_makin_charges = 0
    shipping = 100
    tax = 3
    for i in order_list.values():
        single_product_data = product_list.filter(id = i['product_id']).last()
        single_product = {}
        single_product['id'] = single_product_data['id']
        single_product['name'] = single_product_data['name']
        single_product['image'] = single_product_data['image'].split(',')[0]
        

        if i['diamond_quality'] != 'P':
            diamond_quality = i['diamond_quality']
            diamond_size = i['diamond_size']
        
            dm_obj = diamond_pricing.objects.filter(diamond_quality = diamond_quality,diamond_size = diamond_size).values().last()
            dm_sum = eval(dm_obj['diamond_pricing']) * eval(diamond_size)
        else:
            dm_sum = 0
        

        weight = i['weight'].split('/')
        mt_obj = metal_price.objects.values().last()
        if len(weight) == 1:
            metal_sum = eval(weight[0]) * eval(mt_obj['platinum'])
            making_charges = eval(weight[0]) * eval(mt_obj['making_charges'])
        else:
            metal_sum = eval(weight[0]) * eval(mt_obj['platinum']) + eval(weight[1]) * eval(mt_obj['gold'])
            making_charges = (eval(weight[0]) + eval(weight[1])) * eval(mt_obj['making_charges'])
    
        total = round(dm_sum + metal_sum + making_charges) * eval(i['quantity'])
        final_sub_total = final_sub_total + total
        final_makin_charges = final_makin_charges + making_charges * eval(i['quantity'])
        
        single_product['price'] = total

        products.append(single_product)
    
    res['original_price'] = final_sub_total
    res['tax'] = tax
    res['payment_method'] = 'Online' 
    res['total_price'] = final_sub_total + round(final_sub_total * (tax/100)) + shipping
    res['shipping'] = shipping      
    res['products'] = products
    res['status_bar'] = {
                            'a':True if res['delivery_status'] in ['Placed','On the way','Delivered'] else False,
                            'b':True if res['delivery_status'] in ['Placed','On the way','Delivered'] else False,
                            'c':True if res['delivery_status'] in ['Placed','On the way','Delivered'] else False,
                            'd':True if res['delivery_status'] in ['On the way','Delivered'] else False,
                            'e':True if res['delivery_status'] in ['On the way','Delivered'] else False,
                            'f':True if res['delivery_status'] in ['Delivered'] else False,
                            'g':True if res['delivery_status'] in ['Delivered'] else False,
                        }

    return Response(res)