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
from apiApp.models import product_data
from apiApp.models import user_whishlist,user_data
from apiApp.models import metal_price,diamond_pricing


#----------------------------extra---------------------------------------------------
import simplejson as json

# Create your views here.

@api_view(['POST'])
def categoryPageNew(request,format=None):
    cat_name = request.data['category_name']


    obj = product_data.objects.filter(category = cat_name).values('id','name','image','diamond_quality','actual_price','selling_price','discount','weight','diamond_quality','diamond_size')
    price_obj = metal_price.objects.values().last()
    diamond_obj = diamond_pricing.objects.values()
    # ----------------------- userdefined functions --------------------------------------------
    def func_eval_first_index(value):
        return eval(value)[0][0]
    def func_image_first(value):
        return value.split(',')[0]
    #-------------------------------------------------------------------------------------------
    df = pd.DataFrame(obj)
    df['image'] = df['image'].apply(func_image_first)
    resp = df.to_dict(orient='records')
    res = {
            'category':cat_name,
            'data':resp,
          }
    try:
        token = request.data['token']
        user = user_data.objects.get(token = token)
        try:
            wishlist_array = user_whishlist.objects.filter(user_id = user.id).values_list('product_id',flat=True)
            res['wishlist_array'] = wishlist_array

        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
    except:
        pass

    
    return Response(res)


@api_view(['POST'])
def productDetails(request,format=None):
    id = request.data['product_id']
    obj = product_data.objects.filter(id=id).values().last()
    res = {}
    res['product_id'] = obj['id']
    res['name'] = obj['name']
    res['category'] = obj['category']
    res['gender'] = 'Male' if obj['gender'] == 'M' else ('Female' if obj['gender'] == 'F' else 'Unisex')
    res['size'] = obj['size'].split(',')
    res['weight'] = obj['weight'].split(',')
    res['diamond_quality'] = obj['diamond_quality'].split(',')
    res['diamond_size'] = obj['diamond_size'].split(',') if obj['diamond_size'].split(',')[0] != "nan" else []
    res['image'] = obj['image'].split(',')
    res['discount'] = '10'

    # ---------------------------Pricing---------------------------------------------------------------------
    weight = res['weight'][0].split('/')
    
    if res['diamond_quality'][0] != 'P':
        diamond_quality = res['diamond_quality'][0]
        diamond_size = res['diamond_size'][0]
    
        dm_obj = diamond_pricing.objects.filter(diamond_quality = diamond_quality,diamond_size = diamond_size).values().last()
        dm_sum = eval(dm_obj['diamond_pricing']) * eval(diamond_size)
    else:
        dm_sum = 0
    
    mt_obj = metal_price.objects.values().last()
    if len(weight) == 1:
        metal_sum = eval(weight[0]) * eval(mt_obj['platinum'])
        making_charges = eval(weight[0]) * eval(mt_obj['making_charges'])
    else:
        metal_sum = eval(weight[0]) * eval(mt_obj['platinum']) + eval(weight[1]) * eval(mt_obj['gold'])
        making_charges = (eval(weight[0]) + eval(weight[1])) * eval(mt_obj['making_charges'])

    sum = dm_sum + metal_sum + making_charges
    discount_price = round(sum - sum*0.10)

    res['actual_price'] = round(sum)
    res['selling_price'] = round(discount_price)
    
    res['diamond_charges'] = 'N/A' if dm_sum == 0 else str(round(dm_sum))
    res['metal_charges'] = str(round(metal_sum))
    res['making_charges'] = str(round(making_charges))
    res['discount_price'] = str(round(sum*0.10)) 
    res['total_charges'] = str(round(discount_price))

    return Response(res)


@api_view(['POST'])
def priceCalculation(request,format=None):
    try:
        data = request.data
        diamond_quality = data['diamond_quality']
        diamond_size = data['diamond_size']
        size = data['size']
        weight = data['weight'].split('/')
        metal_obj = metal_price.objects.values().last()
        diamond_obj = diamond_pricing.objects
        
        if diamond_quality != 'P':
            dm_obj = diamond_pricing.objects.filter(diamond_quality = diamond_quality,diamond_size = diamond_size).values().last()
            dm_sum = eval(dm_obj['diamond_pricing']) * eval(diamond_size)
        else:
            dm_sum = 0
        

        mt_obj = metal_price.objects.values().last()
        if len(weight) == 1:
            metal_sum = eval(weight[0]) * eval(mt_obj['platinum'])
            making_charges = eval(weight[0]) * eval(mt_obj['making_charges'])
        else:
            metal_sum = eval(weight[0]) * eval(mt_obj['platinum']) + eval(weight[1]) * eval(mt_obj['gold'])
            making_charges = (eval(weight[0]) + eval(weight[1])) * eval(mt_obj['making_charges'])

        sum = round(dm_sum + metal_sum + making_charges)
        discount_price = round(sum - sum*0.10)

        res = {
                'status':True,
                'selling_price':str(sum),
                'actual_price':str(discount_price)
                }
        res['diamond_charges'] = 'N/A' if dm_sum == 0 else str(round(dm_sum))
        res['metal_charges'] = str(round(metal_sum))
        res['making_charges'] = str(round(making_charges))
        res['discount_price'] = str(round(sum*0.10))
        res['total_charges'] = str(round(discount_price))

        return Response(res)
    except:
        res = {
                'status':False,
                'message':'something went wrong refresh again'
                }
        return Response(res)

