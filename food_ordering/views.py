from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, DeleteView, UpdateView, CreateView
from food_ordering.models import *


class HomePage(TemplateView):
    template_name = 'home.html'


# def best_sells(req):
#     foods = Food.objects.filter(menu_items__order_item__order_status__contains='R')
#     best_foods = foods.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')[:3]
#
#     branches = Branch.objects.filter(menu_items__order_item__order_status__contains='R')
#     best_branches = branches.annotate(total_sum=Sum('menu_items__order_item__quantity')).order_by('-total_sum')[:3]
#
#     context = {'best_foods': best_foods, 'best_branches': best_branches}
#     return render(req, 'home.html', context)


'''admin panel views'''


class FoodList(ListView):
    model = Food
    template_name = 'food_ordering/food_list.html'


class FoodDetail(DetailView):
    model = Food
    template_name = 'food_ordering/food_detail.html'


class FoodUpdate(UpdateView):
    model = Food
    fields = '__all__'
    template_name = 'food_ordering/food_edit.html'
    success_url = reverse_lazy('food_list')


class FoodDelete(DeleteView):
    model = Food
    template_name = 'food_ordering/food_delete.html'
    success_url = reverse_lazy('food_list')


class FoodCreate(CreateView):
    model = Food
    template_name = 'food_ordering/add_food.html'
    fields = '__all__'
    success_url = reverse_lazy('add_food')


class CategoryCreate(CreateView):
    model = Category
    template_name = 'food_ordering/add_category.html'
    fields = '__all__'
    success_url = reverse_lazy('add_category')


'''end Admin panel'''
