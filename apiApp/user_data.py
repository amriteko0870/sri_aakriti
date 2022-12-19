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
from apiApp.models import user_data

#----------------------------extra---------------------------------------------------
import simplejson as json


@api_view(['POST'])
def profileView(request,format=None):
    token = request.data['token']
    try:
        user = user_data.objects.get(token = token)
        res = {
                'status':True,
                'message':'Response created successfully',
                'name': user.name,
                'gender':user.gender,
                'dob':user.dob,
                'email':user.email,
                'phone_no':user.phone_no,
                'phone_code':user.phone_code,
        }
    except:
        res = {
                'status':False,
                'message': 'Something went wrong'        
              }
    return Response(res)


@api_view(['PUT'])
def profileEdit(request,formt=None):
    name = request.data['name']
    gender = request.data['gender']
    dob = request.data['dob']
    email = request.data['email']
    phone_code = request.data['phone_code']
    phone_no = request.data['phone_no']
    token = request.data['token']

    try:
        user_data.objects.get(token = token)
        user_data.objects.filter(token = token).update(
                                                        name = name,
                                                        email = email,
                                                        gender = gender,
                                                        dob = dob,
                                                        phone_code = phone_code,
                                                        phone_no = phone_no,
                                                      )
        res = {
               'status':True,
               'message': 'Profile updated successfully'
              }
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
    return Response(res)