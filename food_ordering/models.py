from django.db import models
from account.models import *


class Restaurant(models.Model):
    name = models.CharField(max_length=100)


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class MealCategory(models.Model):
    class Meta:
        verbose_name_plural = 'MealCategories'

    BREAKFAST = 'B'
    LUNCH = 'L'
    DINNER = 'D'
    MEAL_CATEGORIES = [
        (BREAKFAST, 'breakfast'),
        (LUNCH, 'lunch'),
        (DINNER, 'dinner')
    ]
    name = models.CharField(max_length=1, choices=MEAL_CATEGORIES)

    def __str__(self):
        return self.name


class Branch(models.Model):
    class Meta:
        verbose_name_plural = 'Branches'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='branches')
    manager = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='branches')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    meal_category = models.ManyToManyField(MealCategory, blank=True, related_name='foods')
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='food_images/')
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

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
    ORDERED = 'O'
    RECORDED = 'R'
    SENT = 'S'
    DELIVERED = 'D'
    ORDER_STATUS = [
        (ORDERED, 'ordered'),
        (RECORDED, 'recorded'),
        (SENT, 'sent'),
        (DELIVERED, 'delivered')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer')
    status = models.CharField(max_length=1, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_item')
    menu_item = models.ManyToManyField(MenuItem, related_name='order_item')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.id
