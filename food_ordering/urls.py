from django.urls import path
from food_ordering.views import *

urlpatterns = [
    # public urls
    path('', MenuItemList.as_view(), name='home'),
    path('search/', searchbar, name='search'),
    path('public_branch_menu/<int:pk>/', PublicBranchMenu.as_view(), name='public_branch_menu'),
    path('food_order/<int:pk>/', food, name='food'),
    path('cart/', cart, name='cart'),
    path("cart/orderitem_delete/<int:pk>/", OrderItemDelete.as_view(), name="orderitem_delete"),
    path("cart/orderitem_edit/<int:pk>/", OrderItemEdit.as_view(), name="orderitem_edit"),

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
    path('add_address/', CustomerAddressCreate.as_view(), name='add_address'),
    path('address/<int:pk>/address_edit/', CustomerAddressUpdate.as_view(), name='address_edit'),
    path('address/<int:pk>/address_delete/', CustomerAddressDelete.as_view(), name='address_delete'),

    # manager urls
    path('add_menuItem/', MenuItemCreate.as_view(), name='add_menuItem'),
    path('branch_menu/', BranchMenu.as_view(), name='branch_menu'),
    path('edit_menuItem/<int:pk>/', MenuItemUpdate.as_view(), name='edit_menuItem'),
    path('delete_menuItem/<int:pk>/', MenuItemDelete.as_view(), name='delete_menuItem'),
    path('request_list/', BranchOrderList.as_view(), name='request_list'),
    path('edit_request_status/<int:pk>/', BranchEditOrderStatus.as_view(), name='edit_request_status'),

]
