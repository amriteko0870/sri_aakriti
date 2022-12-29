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


#----------------------------extra---------------------------------------------------
import simplejson as json

# Create your views here.

@api_view(['POST'])
def categoryPageNew(request,format=None):
    cat_name = request.data['category_name']


    obj = product_data.objects.filter(category = cat_name).values('id','name','image','diamond_quality','actual_price','selling_price','discount')
    # ----------------------- userdefined functions --------------------------------------------
    def func_eval_first_index(value):
        return eval(value)[0][0]
    def func_image_first(value):
        return value.split(',')[0]
    #-------------------------------------------------------------------------------------------
    df = pd.DataFrame(obj)
    # df['actual_price'] = df['actual_price'].apply(func_eval_first_index)
    # df['selling_price'] = df['selling_price'].apply(func_eval_first_index)
    df['actual_price'] = df['actual_price']
    df['selling_price'] = df['selling_price']
    df['image'] = df['image'].apply(func_image_first)
    
    resp = df.to_dict(orient='records')

    res = {
            'category':cat_name,
            'data':resp,
          }
    try:
        token = request.data['token']
        try:
            user = user_data.objects.get(token = token)
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
    res['gender'] = 'Male' if obj['gender'] == 'M' else ('Female' if obj['gender'] == 'F' else 'Unisex')
    res['size'] = obj['size'].split(',')
    res['weight'] = obj['weight'].split(',')
    res['diamond_quality'] = obj['diamond_quality'].split(',')
    # res['actual_price'] = eval(obj['actual_price'])
    # res['selling_price'] = eval(obj['selling_price'])
    res['discount'] = obj['discount']
    res['image'] = obj['image'].split(',')

    res['actual_price'] = obj['actual_price']
    res['selling_price'] = obj['selling_price']
    return Response(res)

# def index(request):
#     product_data.objects.all().delete()
#     df = pd.read_excel('EKO Sri aakriti Products Details (2).xlsx')
#     for i in range(df.shape[0]):
#         name = list(df['Product Name'])[i]
#         category = 'rings'
#         gender = 'M' if list(df['M or F'])[i] == 'GENTS' else 'F' if list(df['M or F'])[i] == 'LADIES' else 'U'
#         diamond_quality = list(df['Diamond Quality'])[i]
#         size = list(df['Size'])[i]
#         weight = list(df['Weight (PT950/K18)'])[i]
#         diamond_size = list(df['Diamond  Size'])[i]
#         diamond_peice = list(df['Diamond pcs'])[i]
#         diamond_wight = list(df['Diamond Wts'])[i]
#         status = 'true'
#         data = product_data(
#                         name = name,
#                         category = category,
#                         gender = gender,
#                         diamond_quality = diamond_quality,
#                         size = size,
#                         weight = weight,
#                         diamond_size = diamond_size,
#                         diamond_peice = diamond_peice,
#                         diamond_wight = diamond_wight,
#                         status = status,
#                     )
#         data.save() 
#         print(i)
#     return HttpResponse('Hello')
