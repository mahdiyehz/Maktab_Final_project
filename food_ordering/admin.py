from django.contrib import admin
from food_ordering.models import *


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'manager', 'category', 'name', 'city', 'description']
    list_display_links = ['name']
    list_editable = ['description']
    list_filter = ['city', 'category']
    search_fields = ('name', 'category')
    list_per_page = 10


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    exclude = ('description',)
    list_display = ['category', 'name', 'description']
    list_display_links = ['name']
    list_editable = ['category']
    list_filter = ['category']
    search_fields = ('name', 'meal_category')
    list_per_page = 10


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['food', 'branch', 'price']
    list_display_links = ['food']
    list_editable = ['price']
    search_fields = ('price',)
    list_filter = ['branch']
    list_per_page = 5


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Customer', {
            'fields': ('customer',)
        }),
        ('Status', {
            'classes': ('collapse',),
            'fields': ('status',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Order', {
            'fields': ('order',)
        }),
        ('Menu', {
             'classes': ('collapse',),
             'fields': ('menu_item',)
         }),
        ('Quantity', {
            'description': "It's show the quantity of customer's order from this item",
            'fields': ('quantity',)
        }),
    )


admin.site.register(Restaurant)
admin.site.register(Category)
admin.site.register(MealCategory)
