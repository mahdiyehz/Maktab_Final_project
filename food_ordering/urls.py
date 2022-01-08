from django.urls import path
from food_ordering.views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('<int:pk>/edit/', FoodUpdate.as_view(), name='food_edit'),
    path('<int:pk>/', FoodDetail.as_view(), name='food_detail'),
    path('<int:pk>/delete/', FoodDelete.as_view(), name='food_delete'),
    path('add_food/', FoodCreate.as_view(), name='add_food'),
    path('add_category/', CategoryCreate.as_view(), name='add_category'),
    path('food_list/', FoodList.as_view(), name='food_list'),
]
