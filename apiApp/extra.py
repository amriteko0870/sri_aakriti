# @api_view(['GET'])
# def navbar(request,format=None):
#     df = pd.read_csv('sri_akriti.csv')
#     titles = list(set(list(df['Category'])))
#     nav = []
#     for i in range(len(titles)):
#         res = {}
#         res['title'] = titles[i]
#         res['id'] = i
#         res['routes'] = '/single-category/'+titles[i]
#         res['sub'] = ['SHOP BY STYLE','SHOP FOR WHOM','GIFTING']
#         sub_sub = []
#         for k in res['sub']:
#             if k == 'SHOP BY STYLE':
#                 l = []
#                 for j in list(set(list(df.loc[df['Category'] == titles[i]]['Sub Category']))):
#                     l.append({'link_name':j,'link_path':"/"+j})
#                 sub_sub.append(l)
#             elif k == 'SHOP FOR WHOM':
#                 l = []
#                 for j in list(set(list(df.loc[df['Category'] == titles[i]]['Gender']))):
#                     l.append({'link_name':j,'link_path':"/"+j})
#                 sub_sub.append(l)
#             else:
#                 l = [
#                         {
#                         "link_name": "Birthday Gift",
#                         "link_path": "/birthday-gift"
#                         },
#                         {
#                         "link_name": "Aniversary Gift",
#                         "link_path": "/aniversary-gift"
#                         },
#                         {
#                         "link_name": "Valentines Day Gift",
#                         "link_path": "/valentines-gift"
#                         },
#                         {
#                         "link_name": "Personal Gift",
#                         "link_path": "/personal-gift"
#                         }
#                     ]
#                 sub_sub.append(l)
#         res['sub_sub'] = sub_sub
#         nav.append(res)
#     res = {}
#     res['title'] = 'COLLECTION'
#     res['id'] = 11
#     res['routes'] = '/single-category/COLLECTION'
#     res['sub'] = ['SHOP BY STYLE','SHOP FOR WHOM','GIFTING']
#     sub_sub = []
#     for k in res['sub']:
#         if k == 'SHOP BY STYLE':
#             l = []
#             for j in list(set(list(df['Sub Category']))):
#                 l.append({'link_name':j,'link_path':"/"+j})
#             sub_sub.append(l[:6])
#         elif k == 'SHOP FOR WHOM':
#             l = []
#             for j in list(set(list(df['Gender']))):
#                 l.append({'link_name':j,'link_path':"/"+j})
#             sub_sub.append(l)
#         else:
#             l = [
#                     {
#                     "link_name": "Birthday Gift",
#                     "link_path": "/birthday-gift"
#                     },
#                     {
#                     "link_name": "Aniversary Gift",
#                     "link_path": "/aniversary-gift"
#                     },
#                     {
#                     "link_name": "Valentines Day Gift",
#                     "link_path": "/valentines-gift"
#                     },
#                     {
#                     "link_name": "Personal Gift",
#                     "link_path": "/personal-gift"
#                     }
#                 ]
#             sub_sub.append(l)
#     res['sub_sub'] = sub_sub
#     nav.append(res)
#     nav1 = [{
#       "title": "ABOUT US",
#       "id": 6,
#       "routes": "/about-us"
#     },
#     {
#       "title": "ACCOUNT",
#       "id": 7,
#       "routes": "/account"
#     },
#     {
#       "title": "WISHLIST",
#       "id": 8,
#       "routes": "/wishlist"
#     },
#     {
#       "title": "STORE",
#       "id": 9,
#       "routes": "/store"
#     }]
#     nav = nav + nav1
#     return Response(nav)
