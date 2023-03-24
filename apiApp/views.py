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

    if cat_name == 'collection':
       obj = product_data.objects.values('id','name','image','diamond_quality','discount','weight','diamond_quality','diamond_size','category') 
    else:
        obj = product_data.objects.filter(category = cat_name).values('id','name','image','diamond_quality','discount','weight','diamond_quality','diamond_size','category')
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
    res['image'] = obj['image'].split(',')[0]
    res['image_all'] = obj['image'].split(',')
    res['discount'] = '10'

    # ---------------------------Pricing---------------------------------------------------------------------
    weight = res['weight'][0].split('/')
    
    if res['diamond_quality'][0] != 'P':
        diamond_quality = res['diamond_quality'][0]
        diamond_size = res['diamond_size'][0]
    
        dm_obj = diamond_pricing.objects.filter(diamond_quality = diamond_quality.strip(),diamond_size = diamond_size.strip()).values().last()
        print(diamond_size)
        print(dm_obj)
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


# def index(request):
#     # product_data.objects.all().delete()
#     xls = pd.ExcelFile('EKO Sri aakriti Products Details New.xlsx')
#     df1 = pd.read_excel(xls, 'Rings')
#     df2 = pd.read_excel(xls, 'Bracelet Pt950')
#     df3 = pd.read_excel(xls, 'Necklace PT950 ')
#     df4 = pd.read_excel(xls, 'Earring-Pendents')
#     df1.fillna('0',inplace=True)
#     df2.fillna('0',inplace=True)
#     df3.fillna('0',inplace=True)
#     df4.fillna('0',inplace=True)
#     df = df4
#     try:
#         s = df['Diamond  Size']
#     except:
#         df['Diamond  Size'] = '0.1'
        
#     for i in range(df.shape[0]):
#         name = df['Product Name'][i]
#         category = 'earrings' #necklace' #'bracelets' # rings # earrings
#         gender = df['M or F'][i]
#         diamond_quality = 'P' if df['Diamond Quality'][i] == '0' else df['Diamond Quality'][i]
#         diamond_size = '0.1' if df['Diamond  Size'][i] == '0' else df['Diamond  Size'][i]
#         # size = str(df['Size'][i]).split(',')
#         # weight = str(df['Weight (PT950/K18)'][i]).split(',')
#         # new_size = []
#         # new_weight = []
#         # for j in range(len(size)):
#         #     if weight[j] == '':
#         #         pass
#         #     else:
#         #         new_size.append(size[j])
#         #         new_weight.append(weight[j])
#         size = 'u'
#         weight = str(df['Weight (PT950/K18)'][i])
        
#         data = product_data(
#                                 name = name,
#                                 category = category,
#                                 gender = gender,
#                                 diamond_quality = diamond_quality,
#                                 diamond_size = diamond_size,
#                                 # size = ','.join(new_size),
#                                 # weight = ','.join(new_weight),
#                                 size = size,
#                                 weight = weight,
#                                 status = True,
#                            )
#         data.save()
#         print(i)

#     return HttpResponse('Hello')


# def index(request):
#     products = product_data.objects.values()
#     def img_path(x):
#         return 'media/products/'+x
#     c = 0
#     for i in products:
#         name = i['name']
#         products_list = os.listdir('media/products')
#         df = pd.DataFrame({'images':products_list})
#         df = df.loc[df['images'].str.contains(name, case=False)]
#         df['images'] = df['images'].apply(img_path)
#         if len(list(df['images'])) > 0:
#             images = ','.join(list(df['images']))
#         else:
#             images = 'media/products/notfound.JPG'
#         product_data.objects.filter(id = i['id']).update(image = images)
#         c = c + 1
#         print(c)

#     return HttpResponse('Hello')

def index(request):
    product_data.objects.filter(image = 'media/products/notfound.JPG').delete()
    return HttpResponse('hello world')