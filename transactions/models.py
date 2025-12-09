
from decimal import Decimal
from django.db import models
from django.forms import model_to_dict
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField

from store.models import Item
from accounts.models import Vendor, Customer
from django.contrib.auth.models import User
from django.utils import timezone

# Import Expense model
from .models_expense import Expense

DELIVERY_CHOICES = [("P", "Pending"), ("S", "Successful")]


class Bankaccount(models.Model):
    slug = AutoSlugField(unique=False, populate_from='account_name')
    account_name = models.CharField(max_length=50)
    opening_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0'))
    as_of_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Created Date"
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.account_name} - opening_balance: {self.opening_balance or 'N/A'}, as_of_date: {self.as_of_date}"

# Model for manual service billing items
class ServiceItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

class BankTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),   # Money In
        ('debit', 'Debit'),     # Money Out
    ]

    bank_account = models.ForeignKey(Bankaccount, on_delete=models.CASCADE, null=True, blank=True,)
    sale = models.ForeignKey('Sale', null=True, blank=True, on_delete=models.SET_NULL)
    purchase = models.ForeignKey('Purchase', null=True, blank=True, on_delete=models.SET_NULL)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, null=True, blank=True,)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True, null=True, blank=True,)
    note = models.CharField(max_length=255, null=True, blank=True,)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.transaction_date} id is {self.id}"
    

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.sale and not self.purchase:
            raise ValidationError("Either a sale or a purchase must be linked.")
        if self.sale and self.purchase:
            raise ValidationError("Only one of sale or purchase can be linked.")


class PaymentRecord(models.Model):
    """
    Track partial payments received for Sales, Purchases, and Service Bills.
    Records which bank account received the payment.
    """
    PAYMENT_SOURCE_CHOICES = [
        ('Sale', 'Sale'),
        ('Purchase', 'Purchase'),
        ('Service', 'Service'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('Online', 'Online'),
    ]

    sale = models.ForeignKey('Sale', null=True, blank=True, on_delete=models.CASCADE, related_name='payment_records')
    purchase = models.ForeignKey('Purchase', null=True, blank=True, on_delete=models.CASCADE, related_name='payment_records')
    servicebill = models.ForeignKey('ServiceBillItem', null=True, blank=True, on_delete=models.CASCADE, related_name='payment_records')
    
    receiving_bank_account = models.ForeignKey(Bankaccount, on_delete=models.CASCADE, related_name='received_payments')
    source_bank_account = models.ForeignKey(Bankaccount, null=True, blank=True, on_delete=models.CASCADE, related_name='sent_payments', help_text="Original bank account sending the payment")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_source_type = models.CharField(max_length=20, choices=PAYMENT_SOURCE_CHOICES)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='Cash')
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text="Transaction ID for online payments (UPI, Reference Number, etc.)")
    
    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        source_id = self.sale_id or self.purchase_id or self.servicebill_id
        return f"₹{self.payment_amount} to {self.receiving_bank_account.account_name} on {self.payment_date.strftime('%Y-%m-%d %H:%M')}"



class Sale(models.Model):
    """
    Represents a sale transaction involving a customer.
    """

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Bank', 'Bank'),
    ]

    STATUS_CHOICES = [
    ('Paid', 'Paid'),
    ('Unpaid', 'Unpaid'),
    ('Balance', 'Balance')
    ]



    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sale Date"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
        db_column="customer"
    )
    sub_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )
    tax_percentage = models.FloatField(default=0)
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )
    amount_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )
    bank_account = models.ForeignKey(Bankaccount,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )
    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='Cash'
    )

    status = models.CharField(
    max_length=10,
    choices=STATUS_CHOICES,
    default='Unpaid'
    )
    total_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )
    actual_total_price_before_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )


    

    class Meta:
        db_table = "sales"
        verbose_name = "Sale"
        verbose_name_plural = "Sales"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_instance = None

        if not is_new:
            old_instance = Sale.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        if self.payment_type == 'Bank' and self.bank_account:
            bank = self.bank_account

            # Revert old balance
            if old_instance and old_instance.bank_account == bank:
                bank.opening_balance -= Decimal(str(old_instance.amount_paid))

            # Add new payment
            bank.opening_balance += Decimal(str(self.amount_paid))
            bank.save()

            # Remove old transaction
            if old_instance:
                BankTransaction.objects.filter(sale=old_instance).delete()

            # Log transaction
            BankTransaction.objects.create(
                bank_account=bank,
                sale=self,
                transaction_type='credit',
                amount=Decimal(str(self.amount_paid)),
                note=f"Sale payment received (Sale ID: {self.id})"
            )



    def __str__(self):
        """
        Returns a string representation of the Sale instance.
        """
        return (
            f"Sale ID: {self.id} | "
            f"Grand Total: {self.grand_total} | "
            f"Date: {self.date_added}"
        )

    def sum_products(self):
        """
        Returns the total quantity of products in the sale.
        """
        return sum(detail.quantity for detail in self.saledetail_set.all())
    
    def get_item_descriptions_by_type(self):
        grouped = {"PROCESSOR": [], "RAM": [], "HDD": [], "SSD": []}
        for detail in self.saledetail_set.all():
            if detail.description:
                for part in detail.description.split("<br>"):
                    if "PROCESSOR:" in part:
                        grouped["PROCESSOR"].append(part.strip())
                    elif "RAM:" in part:
                        grouped["RAM"].append(part.strip())
                    elif "HDD:" in part:
                        grouped["HDD"].append(part.strip())
                    elif "SSD:" in part:
                        grouped["SSD"].append(part.strip())
        return grouped
    

    @property
    def type_label(self):
        return "Sale"


class SaleDetail(models.Model):
    """
    Represents details of a specific sale, including item and quantity.
    """

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        db_column="sale",
        related_name="saledetail_set"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.DO_NOTHING,
        db_column="item"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField()
    total_detail = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )

    # ✅ Add this field
    description = models.TextField(blank=True, null=True)

    sell_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, blank=True
    )


    class Meta:
        db_table = "sale_details"
        verbose_name = "Sale Detail"
        verbose_name_plural = "Sale Details"

    def __str__(self):
        """
        Returns a string representation of the SaleDetail instance.
        """
        return (
            f"Detail ID: {self.id} | "
            f"Sale ID: {self.sale.id} | "
            f"Quantity: {self.quantity}"
        )
    

class catogaryitempurchased(models.Model):
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
    serial_no = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_code =  models.CharField(max_length=100,null=True, blank=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_itemspurchased_created'
    )
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_itemspurchased_updated'
    )
    updated_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        String representation of the Ram.
        """
        return f"category: {self.category} ( {self.name} ) X {self.quantity}"

    class Meta:
        verbose_name_plural = 'category_itempurchased'
    


class Itempurchased(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('not_available', 'Not Available'),
        ('replacement', 'Replacement'),
    ]

    slug = AutoSlugField(unique=False, populate_from='name')
    name = models.CharField(max_length=50)
    serialno = models.CharField(max_length=50, unique=False, null=True)
    make_and_models = models.CharField(max_length=100, null=True)
    catogary_item_clone = models.ManyToManyField(catogaryitempurchased, blank=True) 
    smps_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')
    smps_replacement_description = models.TextField(max_length=100,null=True, blank=True)
    motherboard_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')
    motherboard_replacement_description = models.TextField(max_length=100, null=True, blank=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    vendor_name = models.ForeignKey(Vendor, related_name="purchases_Item", on_delete=models.CASCADE, null=True, blank=True)
    purchased_code =  models.CharField(max_length=100,null=True, blank=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='itemspurchased_created'
    )
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='itemspurchased_updated'
    )
    updated_date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.name} - serialno: {self.serialno or 'N/A'}, make_and_models: {self.make_and_models}, id: {self.id}"

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
        catogaryitempurchased.objects.filter(serial_no=self.serialno).delete()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Itemspurchased'
        


class Purchase(models.Model):
    """
    Represents a purchase transaction involving a customer.
    """

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Bank', 'Bank'),
    ]

    STATUS_CHOICES = [
    ('Paid', 'Paid'),
    ('Unpaid', 'Unpaid'),
    ('Balance', 'Balance')
    ]



    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Purchase Date", null=True
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.DO_NOTHING,
        db_column="vendor", null=True
    )
    sub_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    tax_percentage = models.FloatField(default=0)
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    amount_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    bank_account = models.ForeignKey(Bankaccount,
    on_delete=models.SET_NULL,
    null=True,
    blank=True, related_name="bank_acc"
    )
    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='Cash'
    )

    status = models.CharField(
    max_length=10,
    choices=STATUS_CHOICES,
    default='Unpaid'
    )


    

    class Meta:
        db_table = "purchases"
        verbose_name = "Purchase"
        verbose_name_plural = "purchases"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_instance = None

        if not is_new:
            old_instance = Purchase.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        if self.payment_type == 'Bank' and self.bank_account:
            bank = self.bank_account

            # Revert old balance
            if old_instance and old_instance.bank_account == bank:
                bank.opening_balance -= Decimal(str(old_instance.amount_paid))

            # Add new payment
            bank.opening_balance += Decimal(str(self.amount_paid))
            bank.save()

            # Remove old transaction
            if old_instance:
                BankTransaction.objects.filter(purchase=old_instance).delete()

            # Log transaction
            BankTransaction.objects.create(
                bank_account=bank,
                purchase=self,
                transaction_type='credit',
                amount=Decimal(str(self.amount_paid)),
                note=f"Purchase payment received (Purchase ID: {self.id})"
            )



    def __str__(self):
        """
        Returns a string representation of the Purchase instance.
        """
        return (
            f"Purchase ID: {self.id} | "
            f"Grand Total: {self.grand_total} | "
            f"Date: {self.date_added}"
        )

    def sum_products(self):
        """
        Returns the total quantity of products in the purchase.
        """
        return sum(detail.quantity for detail in self.purchasedetail_set.all())
    
    def get_item_descriptions_by_type(self):
        grouped = {"PROCESSOR": [], "RAM": [], "HDD": [], "SSD": []}
        for detail in self.purchasedetail_set.all():
            if detail.description:
                for part in detail.description.split("<br>"):
                    if "PROCESSOR:" in part:
                        grouped["PROCESSOR"].append(part.strip())
                    elif "RAM:" in part:
                        grouped["RAM"].append(part.strip())
                    elif "HDD:" in part:
                        grouped["HDD"].append(part.strip())
                    elif "SSD:" in part:
                        grouped["SSD"].append(part.strip())
        return grouped





# class Sale(models.Model):
#     """
#     Represents a sale transaction involving a customer.
#     """

#     PAYMENT_CHOICES = [
#         ('Cash', 'Cash'),
#         ('Cheque', 'Cheque'),
#         ('Bank', 'Bank'),
#     ]

#     STATUS_CHOICES = [
#     ('Paid', 'Paid'),
#     ('Unpaid', 'Unpaid'),
#     ('Balance', 'Balance')
#     ]



#     date_added = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name="Sale Date"
#     )
#     customer = models.ForeignKey(
#         Customer,
#         on_delete=models.DO_NOTHING,
#         db_column="customer"
#     )
#     sub_total = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.0
#     )
#     grand_total = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.0
#     )
#     tax_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.0
#     )
#     tax_percentage = models.FloatField(default=0)
#     amount_paid = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.0
#     )
#     amount_change = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.0
#     )
#     bank_account = models.ForeignKey(Bankaccount,
#     on_delete=models.SET_NULL,
#     null=True,
#     blank=True
#     )
#     payment_type = models.CharField(
#         max_length=10,
#         choices=PAYMENT_CHOICES,
#         default='Cash'
#     )

#     status = models.CharField(
#     max_length=10,
#     choices=STATUS_CHOICES,
#     default='Unpaid'
#     )


    

#     class Meta:
#         db_table = "sales"
#         verbose_name = "Sale"
#         verbose_name_plural = "Sales"

#     def save(self, *args, **kwargs):
#         is_new = self._state.adding
#         old_instance = None

#         if not is_new:
#             old_instance = Sale.objects.get(pk=self.pk)

#         super().save(*args, **kwargs)

#         if self.payment_type == 'Bank' and self.bank_account:
#             bank = self.bank_account

#             # Revert old balance
#             if old_instance and old_instance.bank_account == bank:
#                 bank.opening_balance -= Decimal(str(old_instance.amount_paid))

#             # Add new payment
#             bank.opening_balance += Decimal(str(self.amount_paid))
#             bank.save()

#             # Remove old transaction
#             if old_instance:
#                 BankTransaction.objects.filter(sale=old_instance).delete()

#             # Log transaction
#             BankTransaction.objects.create(
#                 bank_account=bank,
#                 sale=self,
#                 transaction_type='credit',
#                 amount=Decimal(str(self.amount_paid)),
#                 note=f"Sale payment received (Sale ID: {self.id})"
#             )



#     def __str__(self):
#         """
#         Returns a string representation of the Sale instance.
#         """
#         return (
#             f"Sale ID: {self.id} | "
#             f"Grand Total: {self.grand_total} | "
#             f"Date: {self.date_added}"
#         )

#     def sum_products(self):
#         """
#         Returns the total quantity of products in the sale.
#         """
#         return sum(detail.quantity for detail in self.saledetail_set.all())
    
#     def get_item_descriptions_by_type(self):
#         grouped = {"PROCESSOR": [], "RAM": [], "HDD": [], "SSD": []}
#         for detail in self.saledetail_set.all():
#             if detail.description:
#                 for part in detail.description.split("<br>"):
#                     if "PROCESSOR:" in part:
#                         grouped["PROCESSOR"].append(part.strip())
#                     elif "RAM:" in part:
#                         grouped["RAM"].append(part.strip())
#                     elif "HDD:" in part:
#                         grouped["HDD"].append(part.strip())
#                     elif "SSD:" in part:
#                         grouped["SSD"].append(part.strip())
#         return grouped


# class SaleDetail(models.Model):
#     """
#     Represents details of a specific sale, including item and quantity.
#     """

#     sale = models.ForeignKey(
#         Sale,
#         on_delete=models.CASCADE,
#         db_column="sale",
#         related_name="saledetail_set"
#     )
#     item = models.ForeignKey(
#         Item,
#         on_delete=models.DO_NOTHING,
#         db_column="item"
#     )
#     price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )
#     quantity = models.PositiveIntegerField()
#     total_detail = models.DecimalField(max_digits=10, decimal_places=2)

#     # ✅ Add this field
#     description = models.TextField(blank=True, null=True)

#     class Meta:
#         db_table = "sale_details"
#         verbose_name = "Sale Detail"
#         verbose_name_plural = "Sale Details"

#     def __str__(self):
#         """
#         Returns a string representation of the SaleDetail instance.
#         """
#         return (
#             f"Detail ID: {self.id} | "
#             f"Sale ID: {self.sale.id} | "
#             f"Quantity: {self.quantity}"
#         )
    
class PurchaseDetail(models.Model):
    """
    Represents details of a specific sale, including item and quantity.
    """

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        db_column="purchase",
        related_name="purchasedetail_set"
    )
    item = models.ForeignKey(
        Itempurchased,
        on_delete=models.DO_NOTHING,
        db_column="itempurchase"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField()
    total_detail = models.DecimalField(max_digits=10, decimal_places=2)

    # ✅ Add this field
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "purchase_details"
        verbose_name = "Purchase Detail"
        verbose_name_plural = "Purchase Details"

    def __str__(self):
        """
        Returns a string representation of the SaleDetail instance.
        """
        return (
            f"Detail ID: {self.id} | "
            f"Purchase ID: {self.purchase.id} | "
            f"Quantity: {self.quantity}"
        )

class ServiceBillItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='service_bills', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    item_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    qty = models.PositiveIntegerField(default=1, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tax_amt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0)

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Bank', 'Bank'),
    ]
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Balance', 'Balance'),
    ]
    bank_account = models.ForeignKey(Bankaccount, on_delete=models.SET_NULL, null=True, blank=True)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='Cash')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.0')
    )

    def __str__(self):
        """
        Returns a string representation of the SaleDetail instance.
        """
        return (
            f"Detail ID: {self.id} | "
            f"Customer Name: {self.customer.first_name} | "
            f"Service Name: {self.item_name}"
        )
    

    @property
    def type_label(self):
        return "ServiceBillItem"
