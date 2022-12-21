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
                                quantity = '1'

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
    sub_total = 0
    shipping = 100
    tax = 1.8
    for i in items:
        prod_data = products.filter(id = i['product_id']).last()

        diamond_list = prod_data['diamond_quality'].split(',')
        size_list = prod_data['size'].split(',')

        diamond_index = diamond_list.index(i['diamond_quality'])
        size_index = size_list.index(i['size'])
        
        prod_dict = {
                     'cart_product_id':i['id'],
                     'id':prod_data['id'],
                     'image':prod_data['image'].split(',')[0],
                     'title':prod_data['name'],
                     'price': eval(prod_data['actual_price'])[diamond_index][size_index],
                     'quantity':i['quantity']
                    }
        sub_total = sub_total + (prod_dict['price'] * int(prod_dict['quantity']))
        product_list.append(prod_dict)

    estimated_total = sub_total + shipping + (sub_total*tax/100)
    checkout = {
                'sub_total':{
                                'title':'Sub Total', 
                                'amount': sub_total,
                            },
                'shipping': {
                                'title': 'Shipping',
                                'charges': shipping,
                            },
                'tax': {
                                'title': 'Estimated Tax',
                                'amount': str(tax)+'%',
                        },
                'total': {
                                'title':'Estimated Total',
                                'amount': round(estimated_total,2)
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
                    

        products = product_data.objects.values()
        items = user_cart.objects.filter(user_id = user.id).values()
        product_list = []
        sub_total = 0
        shipping = 100
        tax = 1.8
        for i in items:
            prod_data = products.filter(id = i['product_id']).last()

            diamond_list = prod_data['diamond_quality'].split(',')
            size_list = prod_data['size'].split(',')

            diamond_index = diamond_list.index(i['diamond_quality'])
            size_index = size_list.index(i['size'])
            
            prod_dict = {
                        'cart_product_id':i['id'],
                        'id':prod_data['id'],
                        'image':prod_data['image'].split(',')[0],
                        'title':prod_data['name'],
                        'price': eval(prod_data['actual_price'])[diamond_index][size_index],
                        'quantity':i['quantity']
                        }
            sub_total = sub_total + (prod_dict['price'] * int(prod_dict['quantity']))
            product_list.append(prod_dict)

        estimated_total = sub_total + shipping + (sub_total*tax/100)
        checkout = {
                    'sub_total':{
                                    'title':'Sub Total', 
                                    'amount': sub_total,
                                },
                    'shipping': {
                                    'title': 'Shipping',
                                    'charges': shipping,
                                },
                    'tax': {
                                    'title': 'Estimated Tax',
                                    'amount': str(tax)+'%',
                            },
                    'total': {
                                    'title':'Estimated Total',
                                    'amount': round(estimated_total,2)
                                },
                    }
        res = {
                'status':True,
                'message':'Quantity updated',
                'products':product_list,
                'checkout_data': checkout
            }

        return Response(res)