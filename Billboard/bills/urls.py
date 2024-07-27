from django.urls import path
from .views import *

urlpatterns = [
   path('', BillList.as_view(), name='bill_list'),
   path('bill/<int:pk>/', BillDetail.as_view(), name='bill_detail'),
   path('categories/<int:pk>/', CategoryList.as_view(), name='bill_cat_list'),
   path('categories/<int:pk>/subscribe/', subscribe, name='subscribe'),
   path('create/', BillCreate.as_view(), name='bill_create'),
   path('bill/<int:pk>/update/', BillUpdate.as_view(), name='bill_edit'),
   path('bill/<int:pk>/delete/', BillDelete.as_view(), name='bill_delete'),
   path('respond/<int:pk>/', Respond.as_view(), name='respond'),
   path('mycomments/<int:pk>', CommentList.as_view(), name='mycomments'),
   path('mycomments/<int:pk>/delete/', CommentDelete.as_view(), name='comment_delete'),
   path('confirm/', ConfirmUser.as_view(), name='confirm_user'),
   path('mycomments/<int:pk>/accept/', accept_comment, name='accept_comment'),
]
