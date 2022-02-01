from allauth.account.views import SignupView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from accounts.forms import *


def login_success(request):
    if request.user.is_superuser:
        return redirect("food_list")
    elif request.user.is_staff:
        return redirect('branch_menu')
    else:
        return redirect("home")


class CustomerSignupView (SignupView):
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('account_login')
    template_name = 'account/signup_customer.html'


class ManagerSignupView (SignupView):
    form_class = ManagerRegistrationForm
    success_url = reverse_lazy('account_login')
    template_name = 'account/signup_manager.html'
