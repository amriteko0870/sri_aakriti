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
from django.core.files.storage import FileSystemStorage
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
from apiApp.models import metal_price

#----------------------------extra----------------------------------------------------
import simplejson as json

# Create your views here.

# ----------------------------------- Product ---------------------------------------------------

@api_view(['POST'])
def adminViewAllProducts(request,format=None):
    data = product_data.objects.values('id','name','category')
    res = {
            'status':True,
            'message':'response for all products',
            'data':list(data)[::-1]
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





@api_view(['GET','POST'])
def adminAddNewProduct(request,format=None):
  if request.method == 'GET':
    res = {
              "name": "",
              "gender": "",
              "category": "",
              "category_all":["rings","earings","necklace","bracelets"],
              "discount": "",
              "image_1": False,
              "image_2": False,
              "image_3": False,
              "image_4": False,
              "diamond_quality": "",
              "diamond_quality_all": [
                "GH-VS/SI",
                "EF-VVS",
                "GH-VS/SI & EF-VVS",
                "P"
              ],
              "diamond_size": [],
              "diamond_size_all": diamond_pricing.objects.values_list('diamond_size',flat=True).distinct(),
              "size_weight": []
            }
    return Response(res)
  if request.method == 'POST':
    data = request.data
        
    if data['gender'] != '':
      gender = 'M' if data['gender'] == 'Male' else ( 'F' if data['gender'] == 'Female' else 'U')
    else:
      res = {
              'status':False,
              'message':'Gender Field Required'
            }
      return Response(res)

    name = data['name']
    if name == '':
      res = {
              'status':False,
              'message':'Name Field Required'
            }
      return Response(res)


    category = data['category']
    if category == '':
      res = {
              'status':False,
              'message':'Category Field Required'
            }
      return Response(res)  
    
    
    diamond_quality = data['diamond_quality']
    if diamond_quality == '':
      res = {
              'status':False,
              'message':'Diamond Quality Field Required'
            }
      return Response(res)

    if diamond_quality != 'P':
      diamond_size = data['diamond_size']
      if len(diamond_size) == 0 :
        res = {
              'status':False,
              'message':'Diamond Size Field Required'
              }
        return Response(res)  
    else:
      diamond_size = []
    
    diamond_size = ','.join(diamond_size)

    if len(data['size_weight']) == 0:
      res = {
              'status':False,
              'message':'Size and Weight Field Required'
              }
      return Response(res)
    else:
      size_weight = data['size_weight']
    size_weight = pd.DataFrame(size_weight)
    size = ','.join(list(size_weight['size']))
    weight = ','.join(list(size_weight['weight']))

    

    image = []
    if data['image_1']:
      image.append(data['image_1'])
    if data['image_2']:
      image.append(data['image_2'])
    if data['image_3']:
      image.append(data['image_3'])
    if data['image_4']:
      image.append(data['image_4'])  
    
    if len(image) == 0:
      res = {
              'status':False,
              'message':'Image Field Required'
            }
      return Response(res)  
    
    image = ','.join(image)

    data = product_data(
                          name = name,
                          category = category,
                          image = image,
                          gender = gender,
                          diamond_quality = diamond_quality,
                          diamond_size = diamond_size,
                          size = size,
                          weight = weight,
                          status = True,
                        )
    data.save()
    
    return Response({'status':True,'message':'product added successfully'})


@api_view(['POST'])
def adminEditSingleProduct(request,format=None):
  data = request.data
  prod_obj = product_data.objects.filter(id = data['product_id']).values()
  name = data['name']
  gender = 'M' if data['gender'] == 'Male' else ( 'F' if data['gender'] == 'Female' else 'U')
  category = data['category']
  diamond_quality = data['diamond_quality']
  diamond_size = ','.join(data['diamond_size'])
  image = []
  if data['image_1']:
    image.append(data['image_1'])
  if data['image_2']:
    image.append(data['image_2'])
  if data['image_3']:
    image.append(data['image_3'])
  if data['image_4']:
    image.append(data['image_4'])
  image = ','.join(image)
  size_weight = pd.DataFrame(data['size_weight'])
  size = ','.join(list(size_weight['size']))
  weight = ','.join(list(size_weight['weight']))

  prod_obj.update(
                    name = name,
                    gender = gender,
                    category = category,
                    diamond_quality = diamond_quality,
                    diamond_size = diamond_size,
                    image = image,
                    size = size,
                    weight = weight,

                 )
  res = {
          'status' : True,
          'message':'Product updation successfull'
        }
  return Response(res)


@api_view(['POST'])
def adminAddImageNewProduct(request,format=None):
  if request.method == 'POST':
    file = request.FILES['file']
    img_path = 'products/'
    fs = FileSystemStorage()
    img_path = img_path+file.name
    upload_res = fs.save(img_path, file)
    updated_value  = 'media/'+upload_res
    res = {
            'status':True,
            'file':updated_value
          }
    return Response(res)

@api_view(['POST'])
def adminImageNameUpdate(request,format=None):
  if request.method == 'POST':
    data = request.data
    data1 = request.data['data']
    if data['index'] == 0:
      data1['image_1'] = data['fileName']
    if data['index'] == 1:
      data1['image_2'] = data['fileName']
    if data['index'] == 2:
      data1['image_3'] = data['fileName']
    if data['index'] == 3:
      data1['image_4'] = data['fileName']
    
    return Response(data1)
    
# ----------------------------------- Orders ---------------------------------------------------------------------

@api_view(['GET','PATCH'])
def adminViewAllOrders(request,format=None):
  if request.method == 'GET':
    def emailFromId(x):
      return user_data.objects.filter(id = x).values().last()['email']
    def pincodeFromId(x):
      try:
        return user_address.objects.filter(user_id = x).values().last()['pincode']
      except:
        return ''
    order_obj = order_payment.objects.values('id','user_id','order_amount','admin_accept_status')
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
  
  if request.method == 'PATCH':
    data= request.data
    print(data)
    id = data['id']
    type = data['type']

    order_obj = order_payment.objects.filter(id = id)

    if type == 'a':
      order_obj.update(admin_accept_status = 'a')
      res = {
              'status':True,
              'message':'Order status updated'
            }
    elif type == 'd':
      order_obj.update(admin_accept_status = 'd')
      res = {
              'status':True,
              'message':'Order status updated'
            }
    else:
      res = {
              'status':False,
              'message':'Something went wrong'
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
      return str(round(( eval(w.split('/')[0]) * eval(pp) + eval(w.split('/')[1]) * eval(gp)) * eval(qt)))
    else:
      return str(round(( eval(w.split('/')[0]) * eval(pp)) * eval(qt)))
  def makingPrice(s,w,mp,qt):
    if len(w.split('/')) > 1:
      return str(round(( eval(w.split('/')[0]) * eval(mp) + eval(w.split('/')[1]) * eval(mp)) * eval(qt)))
    else:
      return str(round(( eval(w.split('/')[0]) * eval(mp)) * eval(qt)))
  def subTotal(dc,mc,mkc):
    return str(round(eval(dc) + eval(mc) + eval(mkc)))
  def diamond_size_na(x):
    return 'N/A' if x == 'undefined' else x

  items = order_details.objects.filter(order_id = order_id)\
                               .values('product_id','diamond_quality','diamond_size','size',
                                       'weight','quantity','platinum','gold','making_charges','diamond')
  items = pd.DataFrame(items)
  items['title'] = items['product_id'].apply(productNameFromId)
  items['diamond_quality'] = items['diamond_quality']
  items['diamond_size'] = items['diamond_size'].apply(diamond_size_na)
  items['metal_size'] = items['size']
  items['metal_weight'] = items['weight']
  items['diamond_charges'] = items.apply(lambda x: diamondPrice(x.diamond_quality, x.diamond_size,),axis=1)
  items['metal_charges'] = items.apply(lambda x: metalPrice(x.size, x.weight,x.platinum,x.gold,x.quantity),axis=1)
  items['making_charges_1'] = items.apply(lambda x: makingPrice(x.size, x.weight,x.making_charges,x.quantity),axis=1)
  items['sub_total'] = items.apply(lambda x: subTotal(x.diamond_charges,x.metal_charges,x.making_charges_1),axis=1)
  # items['title'] = items['product_id'].apply(lambda x: check_func(x.weight, x.making_charges),axis=1)
  items.fillna('',inplace=True)
  items = items[['title','diamond_quality','diamond_size','metal_size','metal_weight','diamond_charges','making_charges_1','sub_total']]
  items = items.to_dict(orient='records')  
  res['items'] = list(items)

  return Response(res)


@api_view(['GET','POST'])
def adminAddNewOrder(request,format=None):
  if request.method == 'GET':
    data = {
            "customer_name": "",
            "customer_phone": "",
            "customer_address": "",
            "customer_email": "",
            "grand_total": "0",
            "items": [],
          }
    product_names = product_data.objects.values('id','name')
    data['product_names'] = product_names
    res = { 
            'status':True,
            'data': data,
          }
    return Response(res)
  
  if request.method == 'POST':
    data = request.data
    if data['customer_email'] in user_data.objects.values_list('email',flat=True):
      user = user_data.objects.get(email=data['customer_email'])
    else:
      user_data_data = user_data(
                          name = data['customer_name'],
                          email = data['customer_email'],
                          phone_no = data['customer_phone'],
                      )
      user_data_data.save()
      user = user_data.objects.get(email=data['customer_email'])
      user_address_data = user_address(
                            user_id = user.id,
                            add_line_1 = data['customer_address'],
                            phone_no = user.phone_no,
                          )
      user_address_data.save()
    order_id_list = order_payment.objects.values_list('order_payment_id',flat=True)
    order_payment_id = 'order_'+''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(14))
    while order_payment_id in order_id_list:
      order_payment_id = 'order_'+''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(14))

    order_payment_data = order_payment(
                          user_id = user.id,
                          order_product = user.name,
                          order_amount = data['grand_total'],
                          order_payment_id = order_payment_id,
                          admin_placed = True,
                        )
    order_payment_data.save()
    
    for i in data['items']:
      order_details_data = order_details(
                              order_id = order_payment_data.id,
                              product_id = i['product_id'],
                              size = i['metal_size'],
                              weight = i['metal_weight'],
                              diamond_quality = i['diamond_quality'],
                              diamond_size = i['diamond_size'],
                              quantity = i['quantity'],
                              platinum = i['platinum'],
                              gold = i['gold'],
                              making_charges = i['making_charges_1'],
                              diamond = i['diamond'],
                              shipping = '100',
                              tax = '3',
                          )
      order_details_data.save()
    res = { 
            'status':True,
            'message':'Order placed'
    }
    return Response(res)

      
  

@api_view(['POST'])
def adminCreateOrderSelectProduct(request,format=None):
  if request.method == 'POST':
    product_id = request.data['product_id']
    try:
      product_info = product_data.objects.filter(id = product_id).values().last()
    except:
      res = {
              'status':False,
              'message':'something went wrong, please try again'
            }
      return Response(res)
    
    diamond_quality = product_info['diamond_quality'].split(',')
    diamond_size = product_info['diamond_size'].split(',') if diamond_quality[0] != 'P' else []
    size = product_info['size'].split(',') 
    weight = product_info['weight'].split(',')

    res = {
            'status':True,
            'data': {
                      'diamond_quality': diamond_quality,
                      'diamond_size': diamond_size,
                      'size': size,
                      'weight': weight,
                    }
          }
    return Response(res)


@api_view(['POST'])
def adminCreateOrderGetProductInfo(request,format=None):
    if request.method == 'POST':
      main_data = request.data
      data = main_data['data']
      # items = main_data['items']
      res = {}
      # return Response(data)

      def productNameFromId(x):
        return product_data.objects.filter(id = x).values().last()['name']
      def productImageFromId(x):
        return product_data.objects.filter(id = x).values().last()['image'].split(',')[0]
      def diamondPrice(dq,ds):
        if dq != 'P':
          return str(round(eval(diamond_pricing.objects.filter(diamond_quality = dq.strip(),diamond_size = ds.strip()).values().last()['diamond_pricing']) * eval(ds.strip())))
        else:
          return '0'
      def metalPrice(s,w,pp,gp,qt):
        qt = str(qt)
        if len(w.split('/')) > 1:
          return str(round(( eval(w.split('/')[0]) * eval(pp) + eval(w.split('/')[1]) * eval(gp)) * eval(qt)))
        else:
          return str(round(( eval(w.split('/')[0]) * eval(pp)) * eval(qt)))
      def makingPrice(s,w,mp,qt):
        qt = str(qt)
        if len(w.split('/')) > 1:
          return str(round(( eval(w.split('/')[0]) * eval(mp) + eval(w.split('/')[1]) * eval(mp)) * eval(qt)))
        else:
          return str(round(( eval(w.split('/')[0]) * eval(mp)) * eval(qt)))
      def subTotal(dc,mc,mkc):
        return str(round(eval(dc) + eval(mc) + eval(mkc)))
      def diamond_size_na(x):
        return 'N/A' if x == 'undefined' else x
      def diamondActualPrice(dq,ds):
        if dq != 'P':
          return str(eval(diamond_pricing.objects.filter(diamond_quality = dq.strip(),diamond_size = ds.strip()).values().last()['diamond_pricing']))
        else:
          return '0'
      
      metal_obj = metal_price.objects.values().last()
      try:
        res['product_id'] = data['id']
        res['title'] = productNameFromId(data['id'])
        res['image'] = productImageFromId(data['id'])
        res['diamond_quality'] = data['diamond_quality']
        res['diamond_size'] = data['diamond_size'] if res['diamond_quality'] != 'P' else 'N/A'
        res['metal_size'] = data['size']
        res['metal_weight'] = data['weight']
        res['quantity'] = data['quantity']
      except:
        res = {
                'status':False,
                'message':'Value required for every field'
              }
        return Response(res)
      res['diamond_charges'] = diamondPrice(res['diamond_quality'],res['diamond_size'])
      res['metal_charges'] = metalPrice(res['metal_size'],res['metal_weight'],metal_obj['platinum'],metal_obj['gold'],data['quantity'])
      res['making_charges_1'] = makingPrice(res['metal_size'],res['metal_weight'],metal_obj['making_charges'],data['quantity'])
      res['sub_total'] = subTotal(res['diamond_charges'],res['metal_charges'],res['making_charges_1'])
      res['gold'] = metal_obj['gold']
      res['platinum'] = metal_obj['platinum']
      res['making_charges'] = metal_obj['making_charges']
      res['diamond'] = diamondActualPrice(res['diamond_quality'],res['diamond_size'])
      

      # items.append(res)
      print(res)
      res = {
              'status':True,
              'items':res,
            }

      return Response(res)


@api_view(['POST'])
def adminCreateOrderFinalPriceCalculation(request,format=None):
  if request.method == 'POST':
    data = request.data
    sum = 0
    for i in data:
      sum = sum + eval(i['sub_total'])
      sum = round(sum)
    tax = round(sum * 3 / 100)
    sum = tax + sum
    shipping = 100
    res = {
            'status':True,
            'tax':"3%",
            'shipping':str(shipping),
            'grand_total':str(sum)
          }
    return Response(res)