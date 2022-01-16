from django.urls import path
from accounts.views import *

urlpatterns = [
    path('customer_signup/', CustomerSignupView.as_view(), name='customer_signup'),
    path('manager_signup/', ManagerSignupView.as_view(), name='manager_signup'),
]
