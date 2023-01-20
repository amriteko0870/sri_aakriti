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



