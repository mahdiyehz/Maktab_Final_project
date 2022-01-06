import jdatetime
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import *


class Restaurant(models.Model):
    name = models.CharField(max_length=100)


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class MealCategory(models.Model):
    class Meta:
        verbose_name_plural = 'MealCategories'

    class MealCategories(models.TextChoices):
        BREAKFAST = 'BREAKFAST', _('Breakfast')
        LUNCH = 'LUNCH', _('Lunch')
        DINNER = 'DINNER', _('Dinner')
        DRINKS = 'DRINKS', _('Drinks')
        Appetizer = 'APPETIZER', _('Appetizer')
        Dessert = 'DESSERT', _('Dessert')

    name = models.CharField(max_length=10, choices=MealCategories.choices)

    def __str__(self):
        return self.name


class Branch(models.Model):
    class Meta:
        verbose_name_plural = 'Branches'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='branches')
    manager = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='branches')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    is_main = models.BooleanField(verbose_name='main branch')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def created_jalali(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y-%m-%d %H:%M:%S')

    def __str__(self):
        return self.name


class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    meal_category = models.ManyToManyField(MealCategory, related_name='foods')
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='food_images/')
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def created_jalali(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y-%m-%d %H:%M:%S')

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='menu_items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='menu_items')
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.food


class Order(models.Model):

    class OrderStatus(models.TextChoices):
        ORDERED = 'O', _('Ordered')
        RECORDED = 'R', _('Recorded')
        SENT = 'S', _('Sent')
        DELIVERED = 'D', _('Delivered')

    status = models.CharField(max_length=1, choices=OrderStatus.choices)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name='orders', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def created_jalali(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y-%m-%d %H:%M:%S')

    def __str__(self):
        return self.customer.first_name


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_item')
    menu_item = models.ManyToManyField(MenuItem, related_name='order_item')
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.menu_item.food
