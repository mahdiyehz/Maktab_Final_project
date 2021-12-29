from django.db import models
from django.contrib.auth.models import AbstractUser


class Address(models.Model):
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    number = models.PositiveIntegerField()

    def __str__(self):
        return self.city + '_' + self.street


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    address = models.ManyToManyField(Address, blank=True, related_name='users')
    device = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.username


class Customer(CustomUser):
    class Meta:
        proxy = True

    def __str__(self):
        return self.username


class Staff(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Restaurant Manager'
        verbose_name_plural = 'Restaurant Managers'

    def __str__(self):
        return self.username


class Admin(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Site Admin'
        verbose_name_plural = 'Site Admins'

    def __str__(self):
        return self.username
