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
def adminViewAllProducts(request,format=None):
    data = product_data.objects.values('id','name','category')
    res = {
            'status':True,
            'message':'response for all products',
            'data':data
          }
    return Response(res)

# @api_view(['GET'])
# def adminSingleProduct(request,format=None):
#     print(request.data)
#     product_id = request.data['product_id']
#     data = product_data.objects.filter(id = product_id).d