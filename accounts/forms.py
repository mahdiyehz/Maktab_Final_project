from allauth.account.forms import SignupForm
from django import forms
from food_ordering.models import *
from accounts.models import *


class CustomerRegistrationForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'] = forms.CharField(required=True)
        self.fields['street'] = forms.CharField(required=True)
        self.fields['number'] = forms.CharField(required=True)

    def save(self, request):
        city = self.cleaned_data.pop('city')
        street = self.cleaned_data.pop('street')
        number = self.cleaned_data.pop('number')

        user = super().save(request)
        Address.objects.create(city=city, street=street, number=number, customer=user, is_main=True)
        return user

    def clean_number(self):
        cleaned_data = super().clean()
        number = cleaned_data.get('number')
        if int(number) <= 0:
            raise forms.ValidationError('invalid number')
        return number


class ManagerRegistrationForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['restaurant'] = forms.CharField(required=True)
        self.fields['category'] = forms.CharField(required=True)
        self.fields['name'] = forms.CharField(required=True)
        self.fields['description'] = forms.CharField(required=True)
        self.fields['city'] = forms.CharField(required=True)
        self.fields['address'] = forms.CharField(required=True)
        self.fields['is_main'] = forms.BooleanField(label='main branch')

    def save(self, request):
        restaurant = self.cleaned_data.get('restaurant')
        category = self.cleaned_data.get('category')
        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        city = self.cleaned_data.get('city')
        address = self.cleaned_data.get('address')
        is_main = self.cleaned_data.get('is_main')

        user = super().save(request)
        user.is_staff = True
        user.save()
        restaurant1, created = Restaurant.objects.get_or_create(name=restaurant)
        category1, created = Category.objects.get_or_create(name=category)
        Branch.objects.create(manager=user, restaurant=restaurant1, category=category1, name=name,
                              description=description, city=city, address=address, is_main=is_main)
        return user

    def clean_is_main(self):
        cleaned_data = super().clean()
        is_main = cleaned_data.get('is_main')
        restaurant = cleaned_data.get('restaurant')
        if Restaurant.objects.filter(name=restaurant).filter(branches__is_main=True).exists() and is_main:
            raise forms.ValidationError('This restaurant has a main branch')
        return is_main

