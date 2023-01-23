from django.conf.urls.static import static
from django.conf import settings

from django.urls import path

import apiApp.views as views
import apiApp.auth as auth
import apiApp.user_data as user
import apiApp.cart as cart
import apiApp.admin_views as admin_views
import apiApp.checkout as checkout_views
import apiApp.payments as payemnt_views
import apiApp.orders as order_views

urlpatterns = [
    #-------------------Filters------------------------------------
    # path('landingPage',views.landingPage,name='landingPage'),
    # path('categoryPage',views.categoryPage,name='categoryPage'),
    path('categoryPageNew',views.categoryPageNew,name='categoryPageNew'),
    path('productDetails',views.productDetails,name='productDetails'),
    path('priceCalculation',views.priceCalculation,name='priceCalculation'),
    
    
    path('signUp',auth.signUp,name='signUp'),
    path('login',auth.login,name='login'),
    path('index',auth.index,name='index'),
    
    
    path('profileView',user.profileView,name='profileView'),
    path('profileEdit',user.profileEdit,name='profileEdit'),
    path('addressAdd',user.addressAdd,name='addressAdd'),
    path('addressEdit',user.addressEdit,name='addressEdit'),
    path('userWishlist',user.userWishlist,name='userWishlist'),
    path('getUserWishlist',user.getUserWishlist,name='getUserWishlist'),
    

    path('checkout',checkout_views.checkout,name='checkout'),

    path('start_payment',payemnt_views.start_payment,name='start_payment'),
    path('success',payemnt_views.handle_payment_success,name='handle_payment_success'),


    path('order_view',order_views.order_view,name='order_view'),
    path('orderDetails',order_views.orderDetails,name='orderDetails'),


    path('addToCart',cart.addToCart,name='addToCart'),
    path('getUserCart',cart.getUserCart,name='getUserCart'),
    path('cartQuantityUpdate',cart.cartQuantityUpdate,name='cartQuantityUpdate'),
    path('cartProductDelete',cart.cartProductDelete,name='cartProductDelete'),
    
    
    path('adminViewAllProducts',admin_views.adminViewAllProducts,name='adminViewAllProducts'),
    path('adminSingleProduct',admin_views.adminSingleProduct,name='adminSingleProduct'),
    

    # path('',views.index,name='index'),

] +static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)