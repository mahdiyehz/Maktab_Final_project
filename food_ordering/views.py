from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from food_ordering.models import *
from accounts.models import *

'''home'''


class MenuItemList(ListView):
    model = MenuItem
    template_name = 'home.html'
    context_object_name = 'menu_item'


class MenuItemDetail(DetailView):
    model = MenuItem
    template_name = 'food_ordering/item_detail.html'
    context_object_name = 'item'


class BranchDetail(DetailView):
    model = Branch
    template_name = 'food_ordering/branch_detail.html'


def best_sells(req):
    foods = Food.objects.filter(menu_items__order_item__order_status__contains='RECORDED')
    best_foods = foods.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')[:3]

    branches = Branch.objects.filter(menu_items__order_item__order_status__contains='RECORDED')
    best_branches = branches.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')[:3]

    context = {'best_foods': best_foods, 'best_branches': best_branches}
    return render(req, 'home.html', context)


'''end home'''

'''searchbar'''


def searchbar(request):
    text = request.GET.get('text')
    items = MenuItem.objects.filter(food__name__contains=text)
    context = {'items': items}
    return render(request, 'home.html', context)


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


def product(request, pk):
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
        orders = Order.objects.filter(Q(customer=customer) & Q(status='ORDERED'))

        if orders:
            order_item_existed = OrderItem.objects.filter(order_id=orders).last()

        if order_item_existed:
            existed_food = Food.objects.filter(menu_items__order_item=order_item_existed)
            existed_branch = Branch.objects.get(menu_items__order_item=order_item_existed)

            if selected_food in existed_food:
                context = {'food': item, 'message': 'this item already exist!'}
                return render(request, 'food_ordering/product.html', context)

        if existed_branch and not selected_branch.name == existed_branch.name:
            context = {'food': item, 'message': 'you can only order from one branch'}
            return render(request, 'food_ordering/product.html', context)

        elif item.quantity >= int(request.POST['quantity']):
            order, created = Order.objects.get_or_create(customer=customer, status='ordered')
            order_item, created = OrderItem.objects.get_or_create(order_id=order, menu_item_id=item, quantity=1)
            order_item.quantity = request.POST['quantity']
            order_item.save()
            return redirect('cart')
        else:
            context = {'food': item, 'message': 'Sorry! Not enough quantity'}
            return render(request, 'food_ordering/product.html', context)
    context = {'food': item}
    return render(request, 'food_ordering/product.html', context)


def cart(request):
    if request.user.is_authenticated:
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
                    order = Order.objects.filter(customer=customer, status='ORDERED').last()

    else:
        device = request.COOKIES['device']
        customer, created = Customer.objects.get_or_create(device=device, email=device)

    order, created = Order.objects.get_or_create(customer=customer, status='ordered')
    context = {'order': order}
    return render(request, 'food_ordering/cart.html', context)


'''end Order and Cart'''


'''customer panel'''

# todo:better practice:with js:)


class CustomerAddressCreate(LoginRequiredMixin, CreateView):
    model = Address
    fields = ['city', 'street', 'number']
    template_name = 'food_ordering/customer/add_address.html'
    success_url = 'address_list'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.customer = self.request.user
        obj.save()
        return super(CustomerAddressCreate, self).form_valid(form)


class CustomerAddressList(LoginRequiredMixin, ListView):
    model = Address
    fields = '__all__'
    template_name = 'food_ordering/customer/address_list.html'
    context_object_name = 'address_list'

    def get_queryset(self):
        query = Address.objects.filter(customer=self.request.user)
        return query

    # def test_func(self):
    #     return self.request.user.username == Address.customer.username

    def handle_no_permission(self):
        return redirect('home')


class CustomerAddressUpdate(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['city', 'street', 'number', 'is_main']
    template_name = 'food_ordering/customer/address_edit.html'
    success_url = reverse_lazy('customer_order')

    # def test_func(self):
    #     return self.request.user.username == Address.customer.username

    def handle_no_permission(self):
        return redirect('home')


class CustomerAddressDelete(LoginRequiredMixin, DeleteView):
    model = Address
    fields = '__all__'
    template_name = 'food_ordering/customer/address_delete.html'
    success_url = reverse_lazy('customer_order')

    def get_object(self, queryset=None):
        obj = super(CustomerAddressDelete, self).get_object()
        if obj.is_main:
            raise Http404
        return obj

    # def test_func(self):
    #     return self.request.user.username == Address.customer.username

    def handle_no_permission(self):
        return redirect('home')


class CustomerOrderList(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = 'food_ordering/customer/customer_panel.html'
    context_object_name = 'order_item'

    def get_queryset(self):
        query = OrderItem.objects.filter(order__customer=self.request.user)
        return query

    # def test_func(self):
    #     return self.get_queryset().filter(order__customer=self.request.user)

    def handle_no_permission(self):
        return redirect('home')


'''end Customer panel'''


'''Restaurant panel'''


class MenuItemCreate(LoginRequiredMixin, CreateView):
    model = MenuItem
    fields = ['food', 'price', 'quantity']
    template_name = 'food_ordering/manager/add_menu_item.html'
    success_url = reverse_lazy('manager_panel')

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


class BranchMenu(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'food_ordering/manager/branch_menu.html'
    context_object_name = 'menu_item'

    def get_queryset(self):
        query = MenuItem.objects.filter(branch=self.request.user.branch)
        return query

    # def test_func(self):
    #     return self.request.user.username == MenuItem.branch.manager.username

    def handle_no_permission(self):
        return redirect('home')


class MenuItemUpdate(LoginRequiredMixin, UpdateView):
    model = MenuItem
    template_name = 'food_ordering/manager/branch_edit.html'
    fields = ['price', 'quantity']
    success_url = reverse_lazy('branch_menu')

    # def test_func(self):
    #     return self.request.user.username == MenuItem.branch.manager.username

    def handle_no_permission(self):
        return redirect('home')


class MenuItemDelete(LoginRequiredMixin, DeleteView):
    model = MenuItem
    fields = '__all__'
    template_name = 'food_ordering/manager/menu_item_delete.html'
    context_object_name = 'item'
    success_url = reverse_lazy('branch_menu')


class BranchOrderList(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = 'food_ordering/manager/branch_requests.html'
    context_object_name = 'order_item'

    def get_queryset(self):
        query = OrderItem.objects.filter(menu_item__branch=self.request.user.branch)
        return query

    # def test_func(self):
    #     return self.request.user.username == OrderItem.menu_item.branch.manager.username

    def handle_no_permission(self):
        return redirect('home')


class BranchEditOrderStatus(LoginRequiredMixin, UpdateView):
    model = Order
    fields = ('status',)
    template_name = 'food_ordering/manager/edit_request_status.html'
    success_url = reverse_lazy('request_list')

    # def test_func(self):
    #     return self.request.user.username == Order.order_item.menu_item.branch.manager.username

    def handle_no_permission(self):
        return redirect('home')


'''end Restaurant panel'''
