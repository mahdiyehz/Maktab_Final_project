from django.contrib import admin
from account.models import *


@admin.register(Customer)
class CustomerProxyAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email']
    list_display_links = ['id']
    list_editable = ['username']
    search_fields = ['username', 'email']
    empty_values_display = '___'
    list_filter = ('address',)
    list_per_page = 10

    def get_queryset(self, request):
        return Customer.objects.filter(is_staff=False)


@admin.register(Staff)
class StaffProxyAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email']
    list_display_links = ['id']
    list_editable = ['username']
    search_fields = ['username', 'email']
    list_per_page = 10

    def get_queryset(self, request):
        return Staff.objects.filter(is_staff=True, is_superuser=False)


@admin.register(Admin)
class AdminProxyAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email']
    list_display_links = ['id']
    list_editable = ['username']
    search_fields = ['username', 'email']

    def get_queryset(self, request):
        return Admin.objects.filter(is_superuser=True)


admin.site.register(CustomUser)
admin.site.register(Address)
