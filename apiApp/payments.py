import json

import razorpay
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apiApp.models import order_payment,order_details
from apiApp.models import user_data,user_cart
from apiApp.models import metal_price,diamond_pricing

from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
def start_payment(request):
    amount = request.data['amount']
    name = request.data['name']
    token = request.data['token']
    try:
        user = user_data.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)

    client = razorpay.Client(auth=('rzp_test_gHJS0k5aSWUMQc', '8hPVwKRnj4DZ7SB1wyW1miaf'))

    payment = client.order.create({"amount": int(amount) * 100, 
                                   "currency": "INR", 
                                   "payment_capture": "1"})

    order = order_payment(order_product=name, 
                  order_amount=amount, 
                  order_payment_id=payment['id'],
                  user_id = user.id,
                  admin_placed = False)
    order.save()

    order_id = order.id

    order_data = order_payment.objects.filter(id = order_id).values().last()

    """order response will be 
    {'id': 17, 
    'order_date': '23 January 2021 03:28 PM', 
    'order_product': '**product name from frontend**', 
    'order_amount': '**product amount from frontend**', 
    'order_payment_id': 'order_G3NhfSWWh5UfjQ', # it will be unique everytime
    'isPaid': False}"""

    data = {
        "payment": payment,
        "order": order_data
    }
    return Response(data)



@csrf_exempt
@api_view(['POST'])
def handle_payment_success(request):
    res = json.loads(request.data["response"])

    """res will be:
    {'razorpay_payment_id': 'pay_G3NivgSZLx7I9e', 
    'razorpay_order_id': 'order_G3NhfSWWh5UfjQ', 
    'razorpay_signature': '76b2accbefde6cd2392b5fbf098ebcbd4cb4ef8b78d62aa5cce553b2014993c0'}
    this will come from frontend which we will use to validate and confirm the payment
    """

    ord_id = res['razorpay_order_id']
    raz_pay_id = res['razorpay_payment_id']
    raz_signature = res['razorpay_signature']

    # # res.keys() will give us list of keys in res
    # for key in res.keys():
    #     if key == 'razorpay_order_id':
    #         ord_id = res[key]
    #     elif key == 'razorpay_payment_id':
    #         raz_pay_id = res[key]
    #     elif key == 'razorpay_signature':
    #         raz_signature = res[key]

    # get order by payment_id which we've created earlier with isPaid=False
    order = order_payment.objects.get(order_payment_id=ord_id)

    # we will pass this whole data in razorpay client to verify the payment
    data = {
        'razorpay_order_id': ord_id,
        'razorpay_payment_id': raz_pay_id,
        'razorpay_signature': raz_signature
    }

    client = razorpay.Client(auth=('rzp_test_gHJS0k5aSWUMQc', '8hPVwKRnj4DZ7SB1wyW1miaf'))

    # checking if the transaction is valid or not by passing above data dictionary in 
    # razorpay client if it is "valid" then check will return None
    check = client.utility.verify_payment_signature(data)

    if not check:
        order.delete()
        print("Redirect to error url or error page")
        return Response({'error': 'Something went wrong'})
 
    # if payment is successful that means check is None then we will turn isPaid=True
    order.isPaid = True
    order.save()
    
    userId = order.user_id
    orderId = order.id
    cart_data = user_cart.objects.filter(user_id = userId)
    metal_obj = metal_price.objects.values().last()
    diamond_obj = diamond_pricing.objects.values()
    for i in cart_data.values():
        if i['diamond_quality'] != 'P':
            diamond_price = diamond_obj.filter(diamond_quality = i['diamond_quality'],diamond_size = i['diamond_size']).last()['diamond_pricing']
        else:
            diamond_price = '0'
        data = order_details(
                                order_id = orderId,
                                product_id = i['product_id'],
                                size = i['size'],
                                weight = i['weight'],
                                diamond_quality = i['diamond_quality'],
                                diamond_size = i['diamond_size'] if i['diamond_size'] != "nan" else '',
                                quantity = i['quantity'],
                                platinum = metal_obj['platinum'],
                                gold = metal_obj['gold'],
                                making_charges = metal_obj['making_charges'],
                                diamond = diamond_price,
                                shipping = '100',
                                tax = '3'
                            )
        data.save()
    cart_data.delete()
    res_data = {
                    'message': 'payment successfully received!'
               }

    return Response(res_data)



# @csrf_exempt
# @api_view(['POST'])
# def handle_payment_success(request):
#     # request.data is coming from frontend
#     print(request.data)

#     res_data = {
#         'message': 'payment successfully received!'
#     }

#     return Response(res_data)