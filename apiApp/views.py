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

#----------------------------extra---------------------------------------------------
import simplejson as json

# Create your views here.

@api_view(['GET'])
def landingPage(request,format=None):
    landing_page_data = {

    'first_section': {
        'section_image': "media/hero-img.png",
                    },
    'third_section': [
                        {
                            'title': 'NECKLESS COLLECTIONS',
                            'image': 'media/bracelet.png',
                            'route': '/single-category/neckless',
                        },
                        {
                            'title': 'BRACELET COLLECTIONS',
                            'image': 'media/chain.png',
                            'route': '/single-category/bracelet'
                        },
                    ],
    'fourth_section': {
                        'section_title': 'Made to last longer than life',
                        'carousal_images': [
                                                { 'route': '/product-details' , 'image': 'media/ring_1.png'}, 
                                                { 'route': '/product-details' , 'image': 'media/ring_2.png'}, 
                                                { 'route': '/product-details' , 'image': 'media/chain_1.png'}, 
                                                { 'route': '/product-details' , 'image': 'media/chain_2.png'}, 
                                                { 'route': '/product-details' , 'image': 'media/ring_1.png'}, 
                                                { 'route': '/product-details' , 'image': 'media/ring_2.png'}, 
                                                { 'route': '/product-details' , 'image': 'media/chain_1.png'}, 
                                                { 'route': '/product-details' , 'image': 'media/chain_2.png'},
                                            ],
                     },

                        }     

    return Response(landing_page_data)  




@api_view(['POST'])
def categoryPage(request,format=None):
    title = request.data['title']
    desc = "Lorem ipsum dolor sit, amet consectetur adipisicing elit. Atque, laborum odio? Sunt, modi tempora sint reprehenderit corrupti laboriosam molestias consequatur."
    df = pd.read_csv('sri_akriti.csv')
    if title == 'COLLECTION':
        ndf = df
    else:
        ndf = df.loc[df['Category'] == title]

    product = []
    for i in range(ndf.shape[0]):
        d = {
            'product_id':i+1,
            'product_name':list(ndf['Product Name'])[i],
            'price':list(ndf['Offer Price'])[i],
            'image':'media/products/'+list(ndf['Product Name'])[i]+'.png'
        }
        product.append(d)
    res = {
        'category':title,
        'category_details':desc,
        'category_image': 'media/products/'+list(ndf['Product Name'])[i]+'.png',
        'products':product
    }
    return Response(res)


def index(request):
    df = pd.read_csv('new_rings.csv')
    # print(df.columns)
    for i in range(df.shape[0]):
        name = list(df['Product Name'])[i].strip()   
        gender =  list(df['M or F'])[i].strip()
        dq =  list(df['Diamond Quality'])[i].strip()
        size =  list(df['Size'])[i]
        weight =  list(df['Weight'])[i]
        ap =  list(df['Actual Price'])[i]
        sp =  list(df['Selling Price'])[i]
        discount =  list(df['Discount'])[i]
        if name not in product_data.objects.values_list('name',flat=True):
            data = product_data(
                                name = name,
                                image =  'media/products/mock_product.png',
                                gender = gender,
                                diamond_quality = dq,
                                size =  size,
                                weight =  weight,
                                actual_price =  ap,
                                selling_price =  sp,
                                discount =  discount,
                                status = 'Active',
                            )
            data.save()
            print(i)
    return HttpResponse('Hello World')




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
    df['actual_price'] = df['actual_price'].apply(func_eval_first_index)
    df['selling_price'] = df['selling_price'].apply(func_eval_first_index)
    df['image'] = df['image'].apply(func_image_first)
    
    resp = df.to_dict(orient='records')
    res = {
            'category':cat_name,
            'data':resp
          }
    return Response(res)


@api_view(['POST'])
def productDetails(request,format=None):
    id = request.data['product_id']
    obj = product_data.objects.filter(id=id).values().last()
    res = {}
    res['name'] = obj['name']
    res['gender'] = 'Male' if obj['gender'] == 'M' else ('Female' if obj['gender'] == 'F' else 'Unisex')
    res['size'] = obj['size'].split(',')
    res['weight'] = obj['weight'].split(',')
    res['diamond_quality'] = obj['diamond_quality'].split(',')
    res['actual_price'] = eval(obj['actual_price'])
    res['selling_price'] = eval(obj['selling_price'])
    res['discount'] = obj['discount']
    res['image'] = obj['image'].split(',')
    return Response(res)