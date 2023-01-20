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


@api_view(['POST'])
def checkout(request,format=None):
    token = request.data['token']
    try:
        user = user_data.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
    res = {}
    # -------------------------------- Form Part --------------------------------------------------
    form = {}
    form['header'] = {
                        'heading':'Delivery Details'
                     }
    form['content'] = [
                        {
                            "label": "Full Name",
                            "value":user.name,
                        },
                        {
                            "label": "Email ID",
                            "value":user.email,
                        },
                        {
                            "label": "Phone Code",
                            "value":user.phone_code
                        },
                        {
                            "label": "Phone Number",
                            "value":user.phone_no
                        }
                      ]   
    res['form'] = form

    #------------------------ Address Part ---------------------------------------------------------
    address = {}  
    address['header'] = {
                            'heading':'Address'
                        }

    address['content'] = user_address.objects.filter(user_id = user.id)\
                                             .annotate(
                                                        locality = Concat(
                                                                            F('add_line_1'),
                                                                            V(', '),
                                                                            F('add_line_2'),
                                                                            output_field=CharField()
                                                                         )
                                                        # locality = Concat(
                                                        #                     Cast('add_line_1',CharField()),
                                                        #                     V(', '),
                                                        #                     Cast('add_line_2',CharField()),
                                                        #                     output_field=CharField()
                                                        #                  )
                                                      ).values('locality','city','pincode',)
    res['address'] = address

    #------------------- Items & checkout part ------------------------------------------------------
    item = {}
    item['header'] = {
                            'heading':'Item Details'
                     }
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
        single_prod_res['id'] = i['product_id']
        single_prod_res['image'] = prod_data['image']
        single_prod_res['title'] = prod_data['name']
        single_prod_res['qty'] = i['quantity']

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
    
        single_prod_res['price'] = round(dm_sum + metal_sum + making_charges) * eval(i['quantity'])
        product_list.append(single_prod_res)

        final_sub_total = final_sub_total + single_prod_res['price']
        final_makin_charges = final_makin_charges + making_charges

    estimated_total = round(final_sub_total)
    cal_tax = estimated_total * tax //100
    estimated_total = estimated_total + cal_tax + round(shipping)
    checkout = {
                'sub_total':{
                                'title':'Sub Total', 
                                'amount': str(round(final_sub_total)),
                            },
                'making_charges':{
                                'title':'Making Charges', 
                                'amount': str(round(final_makin_charges)),
                            },
                'shipping': {
                                'title': 'Shipping',
                                'amount': str(shipping),
                            },
                'tax': {
                                'title': 'Estimated Tax',
                                'amount': str(tax)+'%',
                        },
                'total': {
                                'title':'Estimated Total',
                                'amount': str(round(estimated_total)//1000)
                            },
                }
    item['content'] = product_list

    res['item'] = item
    res['checkout_data'] = checkout
    
    return Response(res)
    


    