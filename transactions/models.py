from decimal import Decimal
from django.db import models
from django_extensions.db.fields import AutoSlugField

from store.models import Item
from accounts.models import Vendor, Customer

DELIVERY_CHOICES = [("P", "Pending"), ("S", "Successful")]


class Bankaccount(models.Model):
    slug = AutoSlugField(unique=False, populate_from='account_name')
    account_name = models.CharField(max_length=50)
    opening_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0)
    as_of_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Created Date"
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.account_name} - opening_balance: {self.opening_balance or 'N/A'}, as_of_date: {self.as_of_date}"

class BankTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),   # Money In
        ('debit', 'Debit'),     # Money Out
    ]

    bank_account = models.ForeignKey(Bankaccount, on_delete=models.CASCADE)
    sale = models.ForeignKey('Sale', null=True, blank=True, on_delete=models.SET_NULL)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.transaction_type.title()} of {self.amount} on {self.transaction_date}"


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

    # ✅ Add this field
    description = models.TextField(blank=True, null=True)

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
    
        


class Purchase(models.Model):
    """
    Represents a purchase of an item,
    including vendor details and delivery status.
    """

    slug = AutoSlugField(unique=True, populate_from="vendor")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.TextField(max_length=300, blank=True, null=True)
    vendor = models.ForeignKey(
        Vendor, related_name="purchases", on_delete=models.CASCADE
    )
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Delivery Date"
    )
    quantity = models.PositiveIntegerField(default=0)
    delivery_status = models.CharField(
        choices=DELIVERY_CHOICES,
        max_length=1,
        default="P",
        verbose_name="Delivery Status",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Price per item (Ksh)",
    )
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """
        Calculates the total value before saving the Purchase instance.
        """
        self.total_value = self.price * self.quantity
        super().save(*args, **kwargs)
        # Update the item quantity
        self.item.quantity += self.quantity
        self.item.save()

    def __str__(self):
        """
        Returns a string representation of the Purchase instance.
        """
        return str(self.item.name)

    class Meta:
        ordering = ["order_date"]




