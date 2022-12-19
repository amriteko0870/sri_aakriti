from django.conf.urls.static import static
from django.conf import settings

from django.urls import path

import apiApp.views as views
import apiApp.auth as auth
import apiApp.user_data as user

urlpatterns = [
    #-------------------Filters------------------------------------
    path('landingPage',views.landingPage,name='landingPage'),
    path('categoryPage',views.categoryPage,name='categoryPage'),
    path('categoryPageNew',views.categoryPageNew,name='categoryPageNew'),
    path('productDetails',views.productDetails,name='productDetails'),
    
    
    path('signUp',auth.signUp,name='signUp'),
    path('login',auth.login,name='login'),
    
    
    path('profileView',user.profileView,name='profileView'),
    path('profileEdit',user.profileEdit,name='profileEdit'),
    


    path('',views.index,name='index'),

] +static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)