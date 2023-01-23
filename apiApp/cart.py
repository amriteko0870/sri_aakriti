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

#----------------------------extra---------------------------------------------------
import simplejson as json
from apiApp.functions import profile_view


@api_view(['POST'])
def addToCart(request,format=None):
    if request.method == 'POST':
        token = request.data['token']
        product_id = request.data['product_id']
        size = request.data['size']
        diamond_quality = request.data['diamond_quality']
        weight = request.data['weight']
        diamond_size = request.data['diamond_size']
        try:
            user = user_data.objects.get(token = token)
        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
            return Response(res)
        obj = user_cart.objects.filter(user_id = user.id,
                                       product_id = product_id,
                                       size = size,
                                       diamond_quality = diamond_quality).values()
        if len(obj) == 0:
            data = user_cart(
                                user_id = user.id,
                                product_id = product_id,
                                size = size,
                                diamond_quality = diamond_quality,
                                quantity = '1',
                                weight = weight,
                                diamond_size = diamond_size,

                            )
            data.save()
            res = {
                    'status' : True,
                    'message': 'Product added to cart successfully'
                }
        else:
            obj = user_cart.objects.filter(user_id = user.id,
                                       product_id = product_id,
                                       size = size,
                                       diamond_quality = diamond_quality).values().last()
            quantity = int(obj['quantity'])+1
            user_cart.objects.filter(user_id = user.id,
                                       product_id = product_id,
                                       size = size,
                                       diamond_quality = diamond_quality).update(quantity = quantity)
            res = {
                    'status' : True,
                    'message': 'Product already exist, quantity increased'
                  }
        return Response(res)

@api_view(['POST'])
def getUserCart(request,format=None):
    token = request.data['token']
    try:
        user = user_data.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    products = product_data.objects.values()
    items = user_cart.objects.filter(user_id = user.id).values()
    product_list = []
    final_sub_total = 0
    final_makin_charges = 0
    shipping = 100
    tax = 3
    for i in items:
        single_prod_res = {}
        prod_data = products.filter(id = i['product_id']).last()
        single_prod_res['cart_product_id'] = i['id']
        single_prod_res['id'] = i['product_id']
        single_prod_res['image'] = prod_data['image'].split(',')[0]
        single_prod_res['title'] = prod_data['name']
        single_prod_res['qty'] = i['quantity']

        if i['diamond_quality'] != 'P':
            diamond_quality = i['diamond_quality']
            diamond_size = i['diamond_size']
        
            dm_obj = diamond_pricing.objects.filter(diamond_quality = diamond_quality.strip(),diamond_size = diamond_size.strip()).values().last()
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
    
        single_prod_res['price'] = round(dm_sum + metal_sum + making_charges) * eval(i['quantity'])
        product_list.append(single_prod_res)

        final_sub_total = final_sub_total + single_prod_res['price']
        final_makin_charges = final_makin_charges + making_charges * eval(i['quantity'])


    estimated_total = round(final_sub_total)
    cal_tax = estimated_total * tax //100
    estimated_total = estimated_total + cal_tax + round(shipping)
    checkout = {
                'sub_total':{
                                'title':'Sub Total', 
                                'amount': str(round(final_sub_total) - round(final_makin_charges)),
                            },
                'making_charges':{
                                'title':'Making Charges', 
                                'amount': str(round(final_makin_charges)),
                            },
                'shipping': {
                                'title': 'Shipping',
                                'charges': str(shipping),
                            },
                'tax': {
                                'title': 'Estimated Tax',
                                'amount': str(tax)+'%',
                        },
                'total': {
                                'title':'Estimated Total',
                                'amount': str(round(estimated_total))
                            },
                }
    res = {
            'status':True,
            'message':'Cart generated',
            'products':product_list,
            'checkout_data': checkout
          }

    return Response(res)


@api_view(['POST'])
def cartQuantityUpdate(request,format=None):
    if request.method == 'POST':
        token = request.data['token']
        cart_product_id = request.data['cart_product_id']
        update_type = request.data['update_type']
        try:
            user = user_data.objects.get(token = token)
        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
            return Response(res)
        
        if update_type == '+':
            obj = user_cart.objects.filter(user_id = user.id,
                                           id = cart_product_id).values().last()
            quantity = int(obj['quantity'])+1
            user_cart.objects.filter(user_id = user.id,
                                           id = cart_product_id).update(quantity = quantity)
        else:
            obj = user_cart.objects.filter(user_id = user.id,
                                           id = cart_product_id).values().last()
            if int(obj['quantity']) <=1:
                user_cart.objects.filter(user_id = user.id,
                                           id = cart_product_id).delete()
            else:
                quantity = int(obj['quantity'])-1
                user_cart.objects.filter(user_id = user.id,
                                           id = cart_product_id).update(quantity = quantity)
                    
        res = {
                'status':True,
                'message':'Quantity updated'
            }

        return Response(res)


@api_view(['POST'])
def cartProductDelete(request,format=None):
    if request.method == 'POST':
        token = request.data['token']
        cart_product_id = request.data['cart_product_id']
        try:
            user = user_data.objects.get(token = token)
        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
            return Response(res)
        user_cart.objects.filter(id = cart_product_id).delete()
        res = {
                'status':True,
                'message':'product deleted from card'
              }
        return Response(res)