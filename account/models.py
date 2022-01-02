from django.db import models
from django.contrib.auth.models import AbstractUser


class Address(models.Model):
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    number = models.PositiveIntegerField()
    is_main = models.BooleanField(verbose_name='main address')

    def __str__(self):
        return self.city + '_' + self.street


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    device = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.username


class Customer(CustomUser):
    class Meta:
        proxy = True

    def save(self):
        if not self.id:
            self.is_staff = False
            self.is_superuser = False
        super().save()

    def __str__(self):
        return self.username


class Staff(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Restaurant Manager'
        verbose_name_plural = 'Restaurant Managers'

    def save(self):
        if not self.id:
            self.is_staff = True
            self.is_superuser = False
        super().save()

    def __str__(self):
        return self.username


class Admin(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Site Admin'
        verbose_name_plural = 'Site Admins'

    def save(self):
        if not self.id:
            self.is_superuser = True
        super().save()

    def __str__(self):
        return self.username


class CustomerAddress(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='user_address')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='user_address')
