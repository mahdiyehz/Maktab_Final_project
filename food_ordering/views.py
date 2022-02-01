import re
from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Q
from django.http import Http404, HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView, TemplateView
from food_ordering.models import *
from accounts.models import *

'''home'''


class MenuItemList(ListView):
    model = MenuItem
    template_name = 'home.html'
    context_object_name = 'menu_item'

    def get_context_data(self, **kwargs):
        foods = Food.objects.exclude(menu_items__order_item__order__status='ordered')
        best_foods = foods.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')[:3]

        branches = Branch.objects.exclude(menu_items__order_item__order__status='ordered')
        best_branches = branches.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')[:3]

        data = super().get_context_data(**kwargs)
        data['best_foods'] = best_foods
        data['best_branches'] = best_branches

        return data


class MenuItemDetail(DetailView):
    model = MenuItem
    template_name = 'food_ordering/item_detail.html'
    context_object_name = 'item'


class BranchDetail(DetailView):
    model = Branch
    template_name = 'food_ordering/public_menu.html'


# def best_foods(req):
#     foods = Food.objects.exclude(menu_items__order_item__order_status__contains='ordered')
#     best_foods = foods.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')
#     print(best_foods)
#     context = {'best_foods': best_foods}
#     print(context)
#     return render(req, 'home.html', context)
#
#
# def best_branches(req):
#     branches = Branch.objects.exclude(menu_items__order_item__order_status__contains='ordered')
#     best_branches = branches.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')
#
#     context = {'best_branches': best_branches}
#     return render(req, 'home.html', context)


class PublicBranchMenu(ListView):
    model = MenuItem
    template_name = 'food_ordering/public_menu.html'
    context_object_name = 'menu_item'

    def get_queryset(self, **kwargs):
        query = MenuItem.objects.filter(branch=self.kwargs['pk'])
        return query


'''end home'''

'''searchbar'''


def searchbar(request):
    if request.method == 'POST' and request.is_ajax():
        text = request.POST.get('text')
        foods = list(MenuItem.objects.filter(food__name__contains=text).values('pk', 'food__name', 'branch__name', 'branch_id'))
        branches = list(Branch.objects.filter(name__contains=text).values('pk', 'name'))

        return JsonResponse({'foods': foods, 'branches': branches, 'message': 'no result'})
    else:
        return HttpResponseForbidden('<h1>access denied!</h1>')


'''end searchbar'''


'''admin panel views'''


class FoodList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Food
    template_name = 'food_ordering/admin/food_list.html'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('home')


class FoodDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Food
    template_name = 'food_ordering/admin/food_detail.html'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('home')


class FoodUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Food
    fields = '__all__'
    template_name = 'food_ordering/admin/food_edit.html'
    success_url = reverse_lazy('food_list')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('home')


class FoodDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Food
    template_name = 'food_ordering/admin/food_delete.html'
    success_url = reverse_lazy('food_list')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('home')


class FoodCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Food
    template_name = 'food_ordering/admin/add_food.html'
    fields = '__all__'
    success_url = reverse_lazy('add_food')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('home')


class CategoryCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    template_name = 'food_ordering/admin/add_category.html'
    fields = '__all__'
    success_url = reverse_lazy('add_category')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('home')


'''end Admin panel'''


'''Order and Cart'''


def food(request, pk):
    item = MenuItem.objects.get(id=pk)
    selected_branch = item.branch
    selected_food = item.food
    existed_branch = ''
    order_item_existed = ''
    if request.method == 'POST':
        item = MenuItem.objects.get(id=pk)
        selected_branch = item.branch
        if request.user.is_authenticated:
            customer = request.user
        else:
            device = request.COOKIES['device']
            customer, created = Customer.objects.get_or_create(device=device, username=device)
        orders = Order.objects.filter(Q(customer=customer) & Q(status='ordered')).last()

        if orders:
            order_item_existed = OrderItem.objects.filter(order=orders).last()

        if order_item_existed:
            existed_food = Food.objects.filter(menu_items__order_item=order_item_existed)
            existed_branch = Branch.objects.get(menu_items__order_item=order_item_existed)

            if selected_food in existed_food:
                context = {'item': item, 'message': 'this item already exist!'}
                return render(request, 'food_ordering/food.html', context)

        if existed_branch and not selected_branch.name == existed_branch.name:
            context = {'item': item, 'message': 'you can only order from one branch'}
            return render(request, 'food_ordering/food.html', context)

        else:
            if item.quantity >= int(request.POST.get('quantity')):
                order, created = Order.objects.get_or_create(customer=customer, status='ordered')
                order_item, created = OrderItem.objects.get_or_create(order=order, menu_item=item, quantity=1)
                order_item.quantity = request.POST['quantity']
                order_item.save()
                return redirect('cart')
            else:
                context = {'item': item, 'message': 'Sorry! Not enough quantity'}
                return render(request, 'food_ordering/food.html', context)
    context = {'item': item}
    return render(request, 'food_ordering/food.html', context)


def cart(request):
    if request.method == 'POST':
        customer_address = request.POST.get('customer_address')
        pk, city, street, number = customer_address.split(" | ")
        choosen_address = Address.objects.get(pk=pk)
        customer = request.user
        order = Order.objects.filter(customer=customer, status='ordered').update(status='recorded')
        massage = 'successfully!'
        return render(request, 'food_ordering/cart.html', {'massage': massage})

    addresses = ''
    if request.user.is_authenticated:
        addresses = Address.objects.filter(customer=request.user)
        customer = request.user
        device = request.COOKIES['device']
        customer_devise = Customer.objects.filter(device=device, username=device).last()
        order, created = Order.objects.get_or_create(customer=customer, status='ORDERED')
        if customer_devise:
            order_device = Order.objects.filter(customer=customer_devise, status='ORDERED').last()
            if order_device:
                order_items_device = OrderItem.objects.filter(order_id=order_device.id)
                if order_items_device:
                    Order.objects.filter(id=order.id).delete()
                    Order.objects.filter(id=order_device.id).update(customer=customer)
                    Customer.objects.filter(id=customer_devise.id).delete()
                    order = Order.objects.filter(customer=customer, status='ordered').last()

    else:
        device = request.COOKIES['device']
        customer, created = Customer.objects.get_or_create(device=device, username=device)

    order, created = Order.objects.get_or_create(customer=customer, status='ordered')
    context = {'order': order, 'addresses': addresses}
    return render(request, 'food_ordering/cart.html', context)


class OrderItemDelete(DeleteView):
    model = OrderItem
    template_name = 'food_ordering/orderitem_delete.html'
    success_url = reverse_lazy('cart')


class OrderItemEdit(UpdateView):
    model = OrderItem
    fields = ('quantity',)
    template_name = 'food_ordering/orderitem_edit.html'
    success_url = reverse_lazy('cart')


'''end Order and Cart'''


'''customer panel'''


class CustomerAddressCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Address
    fields = ['city', 'street', 'number']
    template_name = 'food_ordering/customer/add_address.html'
    success_url = reverse_lazy('address_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.customer = self.request.user
        obj.save()
        return super(CustomerAddressCreate, self).form_valid(form)

    def test_func(self):
        return not self.request.user.is_superuser and not self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class CustomerAddressList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Address
    fields = '__all__'
    template_name = 'food_ordering/customer/address_list.html'
    context_object_name = 'address_list'

    def get_queryset(self):
        query = Address.objects.filter(customer=self.request.user)
        return query

    def test_func(self):
        return not self.request.user.is_superuser and not self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class CustomerAddressUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Address
    fields = ['city', 'street', 'number']
    template_name = 'food_ordering/customer/address_edit.html'
    success_url = reverse_lazy('address_list')

    def test_func(self):
        return not self.request.user.is_superuser and not self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class CustomerAddressDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Address
    fields = '__all__'
    template_name = 'food_ordering/customer/address_delete.html'
    success_url = reverse_lazy('address_list')

    def get_object(self, queryset=None):
        obj = super(CustomerAddressDelete, self).get_object()
        if obj.is_main:
            raise Http404('you can not delete main address!')
        return obj

    def test_func(self):
        return not self.request.user.is_superuser and not self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class CustomerOrderList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = OrderItem
    template_name = 'food_ordering/customer/customer_panel.html'
    context_object_name = 'order_item'

    def get_queryset(self):
        query = OrderItem.objects.filter(order__customer=self.request.user)
        return query

    def test_func(self):
        return not self.request.user.is_superuser and not self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


'''end Customer panel'''


'''Restaurant panel'''


class MenuItemCreate(LoginRequiredMixin,UserPassesTestMixin, CreateView):
    model = MenuItem
    fields = ['food', 'price', 'quantity']
    template_name = 'food_ordering/manager/add_menu_item.html'
    success_url = reverse_lazy('branch_menu')

    def get_form_class(self):
        form_class = super().get_form_class()
        branch = self.request.user.branch
        foods = branch.menu_items.values_list('food', flat=True).distinct()
        form_class.base_fields.get('food').queryset = Food.objects.exclude(pk__in=foods).filter(category=branch.category)
        return form_class

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.branch = self.request.user.branch
        obj.save()
        return super(MenuItemCreate, self).form_valid(form)

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class BranchMenu(LoginRequiredMixin,UserPassesTestMixin, ListView):
    model = MenuItem
    template_name = 'food_ordering/manager/branch_menu.html'
    context_object_name = 'menu_item'

    def get_queryset(self):
        query = MenuItem.objects.filter(branch=self.request.user.branch)
        return query

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')

class MenuItemUpdate(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = MenuItem
    template_name = 'food_ordering/manager/branch_edit.html'
    fields = ['price', 'quantity']
    success_url = reverse_lazy('branch_menu')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class MenuItemDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MenuItem
    fields = '__all__'
    template_name = 'food_ordering/manager/menu_item_delete.html'
    context_object_name = 'item'
    success_url = reverse_lazy('branch_menu')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class BranchOrderList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = OrderItem
    template_name = 'food_ordering/manager/branch_requests.html'
    context_object_name = 'order_item'

    def get_queryset(self):
        query = OrderItem.objects.filter(menu_item__branch=self.request.user.branch)
        return query

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


class BranchEditOrderStatus(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    fields = ('status',)
    template_name = 'food_ordering/manager/edit_request_status.html'
    success_url = reverse_lazy('request_list')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseForbidden('<h1>access denied!</h1>')


'''end Restaurant panel'''
