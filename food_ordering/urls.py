from django.urls import path
from food_ordering.views import *

urlpatterns = [
    # public urls
    path('', MenuItemList.as_view(), name='home'),
    path('search/', searchbar, name='search'),
    # path('bests/', best_sells, name='bests'),
    path('branch/<int:pk>/', BranchDetail.as_view(), name='branch_detail'),
    path('search/<int:pk>/', MenuItemDetail.as_view(), name='item_detail'),

    # admin urls
    path('food_list/', FoodList.as_view(), name='food_list'),
    path('<int:pk>/edit/', FoodUpdate.as_view(), name='food_edit'),
    path('food/<int:pk>/', FoodDetail.as_view(), name='food_detail'),
    path('<int:pk>/delete/', FoodDelete.as_view(), name='food_delete'),
    path('add_food/', FoodCreate.as_view(), name='add_food'),
    path('add_category/', CategoryCreate.as_view(), name='add_category'),


    # customer urls
    path('customer_order/', CustomerOrderList.as_view(), name='customer_order'),
    path('address/', CustomerAddressList.as_view(), name='address_list'),
    path('address/<int:pk>/address_edit/', CustomerAddressUpdate.as_view(), name='address_edit'),
    path('address/<int:pk>/address_delete/', CustomerAddressDelete.as_view(), name='address_delete'),

    # manager urls
    path('add_menuItem/', MenuItemCreate.as_view(), name='add_menuItem'),
    path('branch_menu/', BranchMenu.as_view(), name='manager_panel'),
    path('edit_menuItem/<int:pk>/', MenuItemUpdate.as_view(), name='edit_menuItem'),
    path('delete_menuItem/<int:pk>/', MenuItemDelete.as_view(), name='delete_menuItem'),
    path('request_list/', BranchOrderList.as_view(), name='request_list'),
    path('edit_request_status/<int:pk>/', BranchEditOrderStatus.as_view(), name='edit_request_status'),

]
