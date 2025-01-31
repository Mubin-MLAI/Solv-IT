"""
Module: models.py

Contains Django models for handling categories, items, and deliveries.

This module defines the following classes:
- Category: Represents a category for items.
- Item: Represents an item in the inventory.
- Delivery: Represents a delivery of an item to a customer.

Each class provides specific fields and methods for handling related data.
"""

from django.db import models
from django.urls import reverse
from django.forms import model_to_dict
from django_extensions.db.fields import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import Vendor
from django.core.validators import MinValueValidator
from django import forms

class catogaryitem(models.Model):
    CATEGORY_CHOICES = [
        ('ssd', 'SSD'),
        ('processor', 'Processor'),
        ('hdd', 'HDD'),
        ('ram', 'RAM'),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,  # Using Category.choices
    )
    name = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """
        String representation of the Ram.
        """
        return f"category: {self.category}"

    class Meta:
        verbose_name_plural = 'category'



class Ram(models.Model):
    """
    Represents a category for items.
    """
    name = models.CharField(max_length=50)
    serial_no = models.CharField(max_length=50, blank= True)
    quantity =  models.PositiveIntegerField()
    unit_price =  models.IntegerField()
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        """
        String representation of the Ram.
        """
        return f"Ram: {self.name}"

    class Meta:
        verbose_name_plural = 'Rams'

class Processor(models.Model):
    """
    Represents a Processor for items.
    """
    
    name = models.CharField(max_length=50)
    serial_no = models.CharField(max_length=50, blank= True)
    quantity =  models.PositiveIntegerField()
    unit_price =  models.IntegerField()
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        """
        String representation of the Processor.
        """
        return f"Processor: {self.name}"

    class Meta:
        verbose_name_plural = 'Processors'

class Hdd(models.Model):
    """
    Represents a Hdd for items.
    """
    
    name = models.CharField(max_length=50)
    serial_no = models.CharField(max_length=50, blank= True)
    quantity =  models.PositiveIntegerField()
    unit_price =  models.IntegerField()
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        """
        String representation of the Hdd.
        """
        return f"Hdd: {self.name}"

    class Meta:
        verbose_name_plural = 'Hdd'

class Sdd(models.Model):
    """
    Represents a Sdd for items.
    """
    
    name = models.CharField(max_length=50)
    serial_no = models.CharField(max_length=50, blank= True)
    quantity =  models.PositiveIntegerField()
    unit_price =  models.IntegerField()
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        """
        String representation of the Sdd.
        """
        return f"Sdd: {self.name}"

    class Meta:
        verbose_name_plural = 'Sdd'
# class M_2(models.Model):
#     name = models.CharField(max_length=50)
#     serial_no = models.CharField(max_length=50, blank= True)
#     quantity =  models.PositiveIntegerField()
#     unit_price =  models.IntegerField()
#     slug = AutoSlugField(unique=True, populate_from='name')

#     def __str__(self):
#         return f"{self.name} - {self.model}"

# class Nvme(models.Model):
#     name = models.CharField(max_length=255)
#     model = models.CharField(max_length=255)
#     capacity = models.PositiveIntegerField(
#         help_text="Capacity in GB",
#         validators=[MinValueValidator(1)]  # Ensures the capacity is at least 1 GB
#     )
#     product_code = models.CharField(max_length=255)

#     def __str__(self):
#         return f"{self.name} - {self.model}"

class Smps(models.Model):
    name = models.CharField(max_length=50)
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        return f"Smps: {self.name}"

    class Meta:
        verbose_name_plural = 'Smps'

class Motherboard(models.Model):
    name = models.CharField(max_length=50)
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        return f"Motherboard: {self.name}"

    class Meta:
        verbose_name_plural = 'Motherboards'



class Item(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('not_available', 'Not Available'),
        ('replacement', 'Replacement'),
    ]

    slug = AutoSlugField(unique=False, populate_from='name')
    name = models.CharField(max_length=50)
    serialno = models.CharField(max_length=50, unique=False, null=True)
    make_and_models = models.CharField(max_length=100, null=True)
    processor = models.CharField(max_length=50, unique=False, null=True)
    processor_qty = models.PositiveIntegerField()
    ram = models.CharField(max_length=50, unique=False, null=True)
    ram_qty = models.PositiveIntegerField()
    hdd = models.CharField(max_length=50, unique=False, null=True)
    hdd_qty = models.PositiveIntegerField()
    ssd = models.CharField(max_length=50, unique=False, null=True)
    ssd_qty = models.PositiveIntegerField()
    smps_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')
    smps_replacement_description = models.TextField(max_length=100,null=True, blank=True)
    motherboard_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')
    motherboard_replacement_description = models.TextField(max_length=100, null=True, blank=True)
    # m_2 = models.ForeignKey('M_2', on_delete=models.CASCADE, null=True, blank=True)
    # nvme = models.ForeignKey('Nvme', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.name} - serialno: {self.serialno or 'N/A'}, make_and_models: {self.make_and_models}"

    def get_absolute_url(self):
        """
        Returns the absolute URL for an item detail view.
        """
        return reverse('item-detail', kwargs={'slug': self.slug})

    def to_json(self):
        product = model_to_dict(self)
        product['id'] = self.id
        product['text'] = self.name
        product['serialno'] = self.serialno.name
        product['ram'] = 1
        product['total_product'] = 0
        return product

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Items'


class Delivery(models.Model):
    """
    Represents a delivery of an item to a customer.
    """
    item = models.ForeignKey(
        Item, blank=True, null=True, on_delete=models.SET_NULL
    )
    customer_name = models.CharField(max_length=30, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    location = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateTimeField()
    is_delivered = models.BooleanField(
        default=False, verbose_name='Is Delivered'
    )

    def __str__(self):
        """
        String representation of the delivery.
        """
        return (
            f"Delivery of {self.item} to {self.customer_name} "
            f"at {self.location} on {self.date}"
        )
