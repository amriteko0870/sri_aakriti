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
from apiApp.models import user_data
from apiApp.models import user_whishlist
from apiApp.models import diamond_pricing
from apiApp.models import order_payment
from apiApp.models import order_details
from apiApp.models import user_address

#----------------------------extra----------------------------------------------------
import simplejson as json

# Create your views here.

@api_view(['POST'])
def adminViewAllProducts(request,format=None):
    data = product_data.objects.values('id','name','category')
    res = {
            'status':True,
            'message':'response for all products',
            'data':data
          }
    return Response(res)

@api_view(['GET'])
def adminSingleProduct(request,format=None):
    id =  request.GET.get('product_id')
    obj = product_data.objects.filter(id=id).values().last()
    res = {}
    res['product_id'] = obj['id']
    res['name'] = obj['name']
    res['gender'] = 'Male' if obj['gender'] == 'M' else ('Female' if obj['gender'] == 'F' else 'Unisex')
    res['category'] = obj['category']
    res['discount'] = obj['discount']
    images = obj['image'].split(',')
    for i in range(1,5):
      try:
        res['image_'+str(i)] = images[i-1]
      except:
        res['image_'+str(i)] = False
      

    res['diamond_quality'] = obj['diamond_quality'] if obj['diamond_quality'] != 'GH-VS/SI,EF-VVS' else 'GH-VS/SI & EF-VVS'
    res['diamond_quality_all'] = ['GH-VS/SI','EF-VVS','GH-VS/SI & EF-VVS','P']
    res['diamond_size'] = obj['diamond_size'].split(',')
    res['diamond_size_all'] = diamond_pricing.objects.values_list('diamond_size',flat=True).distinct()

    size_weight = {
                    'size':obj['size'].split(','),
                    'weight':obj['weight'].split(','),
                  }
    size_weight = pd.DataFrame(size_weight)
    size_weight['id'] = size_weight.index
    size_weight = size_weight.to_dict(orient='records')
    res['size_weight'] = size_weight

    return Response(res)



@api_view(['POST','DELETE'])
def sizeWeight(request,format=None):
  if request.method == 'POST':
    data = request.data
    size_weight = data['size_weight']
    size_weight.append({'size':'','weight':'','id':''})
    size_weight = pd.DataFrame(size_weight)
    size_weight['id'] = size_weight.index
    size_weight = size_weight.to_dict(orient='records')
    data['size_weight'] = size_weight
    return Response(data)
  
  if request.method == 'DELETE':
    data = request.data['data']
    size_wieght_id = request.data['id']
    size_weight = data['size_weight']
    size_weight.pop(size_wieght_id)
    data['size_weight'] = size_weight
    return Response(data)


@api_view(['POST',"DELETE"])
def diamondSize(request,format=None):
  if request.method == 'POST':
    data = request.data['data']
    diamond_size = request.data['diamond_size'] 
    diamond_size_list = data['diamond_size']
    if diamond_size in diamond_size_list:
      res = {
              'status':False,
              'message':'size already present'
            }
      return Response(res)
    else:
      diamond_size_list.append(diamond_size)
      data['diamond_size'] = diamond_size_list
      res = {
              'status':True,
              'data':data
            }
    return Response(res)
  
  if request.method == 'DELETE':
    data = request.data['data']
    index = request.data['index']

    diamond_size = data['diamond_size']
    diamond_size.pop(index)
    data['diamond_size'] = diamond_size
    return Response(data)


@api_view(['GET'])
def adminViewAllOrders(request,format=None):

  def emailFromId(x):
    return user_data.objects.filter(id = x).values().last()['email']
  def pincodeFromId(x):
    try:
      return user_address.objects.filter(user_id = x).values().last()['pincode']
    except:
      return ''
  order_obj = order_payment.objects.values('id','user_id','order_amount')
  if len(order_obj) > 0 : 
    order_obj = pd.DataFrame(order_obj)
    order_obj['email'] = order_obj['user_id'].apply(emailFromId)
    order_obj['pincode'] = order_obj['user_id'].apply(pincodeFromId)
    order_obj = order_obj.to_dict(orient='records')
  else:
    order_obj = []
  res = {
          'status':True,
          'orders': order_obj
        }
  return Response(res)


@api_view(['GET'])
def adminSingleOrder(request,format=None):
  order_id =  request.GET.get('order_id')
  order = order_payment.objects.filter(id = order_id).values().last()
  user = user_data.objects.get(id = order['user_id'])
  address = user_address.objects.get(user_id = user.id)
  res = {}
  res['customer_name'] = user.name
  res['customer_phone'] = user.phone_code+' '+user.phone_no
  res['customer_address'] = address.add_line_1+', '+address.add_line_2+', '+address.landmark+', '+address.city\
                            +', '+address.state+'-'+address.pincode+', '+address.country
  res['customer_email'] = user.email
  res['grand_total'] = order['order_amount']


  def productNameFromId(x):
    return product_data.objects.filter(id = x).values().last()['name']
  def diamondPrice(dq,ds):
    if dq != 'P':
      return str(round(eval(diamond_pricing.objects.filter(diamond_quality = dq.strip(),diamond_size = ds.strip()).values().last()['diamond_pricing']) * eval(ds.strip())))
    else:
      return '0'
  def metalPrice(s,w,pp,gp,qt):
    if len(w.split('/')) > 1:
      return str(round(( eval(w.split('/')[0]) * eval(pp) + eval(w.split('/')) * eval(gp)) * eval(qt)))
    else:
      return str(round(( eval(w.split('/')[0]) * eval(pp)) * eval(qt)))
  def makingPrice(s,w,mp,qt):
    if len(w.split('/')) > 1:
      return str(round(( eval(w.split('/')[0]) * eval(mp) + eval(w.split('/')) * eval(mp)) * eval(qt)))
    else:
      return str(round(( eval(w.split('/')[0]) * eval(mp)) * eval(qt)))
  def subTotal(dc,mc,mkc):
    return str(round(eval(dc) + eval(mc) + eval(mkc)))

  items = order_details.objects.filter(order_id = order_id)\
                               .values('product_id','diamond_quality','diamond_size','size',
                                       'weight','quantity','platinum','gold','making_charges','diamond')
  items = pd.DataFrame(items)
  items['title'] = items['product_id'].apply(productNameFromId)
  items['diamond_quality'] = items['diamond_quality']
  items['metal_size'] = items['size']
  items['metal_weight'] = items['weight']
  items['diamond_charges'] = items.apply(lambda x: diamondPrice(x.diamond_quality, x.diamond_size,),axis=1)
  items['metal_charges'] = items.apply(lambda x: metalPrice(x.size, x.weight,x.platinum,x.gold,x.quantity),axis=1)
  items['making_charges_1'] = items.apply(lambda x: makingPrice(x.size, x.weight,x.making_charges,x.quantity),axis=1)
  items['sub_total'] = items.apply(lambda x: subTotal(x.diamond_charges,x.metal_charges,x.making_charges_1),axis=1)
  # items['title'] = items['product_id'].apply(lambda x: check_func(x.weight, x.making_charges),axis=1)
  items.fillna('',inplace=True)
  items = items[['title','diamond_quality','metal_size','metal_weight','diamond_charges','making_charges_1','sub_total']]
  items = items.to_dict(orient='records')  
  res['items'] = list(items)


  return Response(res)

