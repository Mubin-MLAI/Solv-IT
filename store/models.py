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
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Vendor, Customer

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
        return f"Ram: {self.name} X ({self.quantity})"

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
        return f"Processor: {self.name} X ({self.quantity})"

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
        return f"Hdd: {self.name} X ({self.quantity})"

    class Meta:
        verbose_name_plural = 'Hdd'

class Ssd(models.Model):
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
        return f"Sdd: {self.name} X ({self.quantity})"

    class Meta:
        verbose_name_plural = 'Sdd'

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


class catogaryitem(models.Model):
    CATEGORY_CHOICES = [
        ('ssd', 'SSDs'),
        ('processor', 'Processors'),
        ('hdd', 'HDDs'),
        ('ram', 'RAMs'),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,  # Using Category.choices
    )
    name = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=100, default='Solv-IT')
    quantity = models.IntegerField(default=1, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_lot_code = models.CharField(max_length=100, null=True, blank=True, default=None)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_items_created'
    )
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_items_updated'
    )
    updated_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        String representation of the Ram.
        """
        return f"category: {self.category} ( {self.name} ) X {self.quantity}"

    class Meta:
        verbose_name_plural = 'category_item'

class Item(models.Model):
    STATUS_CHOICES = [
        ('NA', 'NA'),
        ('available', 'Available'),
        ('not_available', 'Not Available'),
        ('replacement', 'Replacement'),
    ]

    slug = AutoSlugField(unique=False, populate_from='name')
    name = models.CharField(max_length=50)
    serialno = models.CharField(max_length=50, unique=False, null=True)
    make_and_models = models.CharField(max_length=100, null=True)
    catogary_item_clone = models.ManyToManyField(catogaryitem, blank=True) 
    smps_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='NA')
    smps_replacement_description = models.TextField(max_length=100,null=True, blank=True)
    motherboard_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='NA')
    motherboard_replacement_description = models.TextField(max_length=100, null=True, blank=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    purchased_code =  models.CharField(max_length=100,null=True, blank=True)
    purchased_type =  models.CharField(max_length=100,null=True, blank=True)
    note = models.TextField(max_length=500, null=True, blank=True, help_text="Additional notes about the item")

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_created'
    )
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_updated'
    )
    updated_date = models.DateTimeField(default=timezone.now)

    customer = models.ForeignKey(Customer,
        on_delete=models.DO_NOTHING, null=True, blank=True,
        db_column="customer"
    )


    def __str__(self):
        return f"{self.name} - serialno: {self.serialno or 'N/A'}, make_and_models: {self.make_and_models}, customer_name: {self.customer.first_name if self.customer else 'N/A'}"

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
    
    def to_select3(self):
        item = {
            "label": self.make_and_models,
            "value": self.id
        }
        return item
    
    def delete(self, *args, **kwargs):
        # Delete associated catogaryitem(s) with the same serialno
        catogaryitem.objects.filter(serial_no=self.serialno).delete()
        super().delete(*args, **kwargs)

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
    


class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=100, unique=True)
    make_and_model = models.CharField(max_length=100, blank=True, null=True)
    processor = models.CharField(max_length=100, blank=True, null=True)
    ram = models.CharField(max_length=100, blank=True, null=True)   # e.g. "8GBX(1), 4GBX(1)"
    hdd = models.CharField(max_length=100, blank=True, null=True)   # e.g. "500GBX(1)"
    ssd = models.CharField(max_length=100, blank=True, null=True)   # e.g. "128GBX(1)"
    smps = models.CharField(max_length=100, blank=True, null=True)  # e.g. "available"
    motherboard = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.serial_no})"

    


