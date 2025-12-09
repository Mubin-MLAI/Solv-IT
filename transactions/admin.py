from django.contrib import admin
from .models import Sale, SaleDetail, Purchase, Bankaccount, BankTransaction, catogaryitempurchased, Itempurchased, PurchaseDetail, Expense, ServiceItem, ServiceBillItem, PaymentRecord

@admin.register(ServiceBillItem)
class ServiceBillItemAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(PurchaseDetail)
class PurchaseDetailAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(catogaryitempurchased)
class CatogaryitempurchasedAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Itempurchased)
class ItempurchasedAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(BankTransaction)
class BankTransAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(Bankaccount)
class BankAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Sale model.
    """
    list_display = (
        'id',
        'customer',
        'date_added',
        'grand_total',
        'amount_paid',
        'amount_change'
    )
    search_fields = ('customer__name', 'id')
    list_filter = ('date_added', 'customer')
    ordering = ('-date_added',)
    readonly_fields = ('date_added',)
    date_hierarchy = 'date_added'

    def save_model(self, request, obj, form, change):
        """
        Save the Sale instance, overriding the default save behavior.
        """
        super().save_model(request, obj, form, change)


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the SaleDetail model.
    """
    list_display = (
        'id',
        'sale',
        'item',
        'price',
        'quantity',
        'total_detail'
    )
    search_fields = ('sale__id', 'item__name')
    list_filter = ('sale', 'item')
    ordering = ('sale', 'item')

    def save_model(self, request, obj, form, change):
        """
        Save the SaleDetail instance, overriding the default save behavior.
        """
        super().save_model(request, obj, form, change)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Purchase model (linked to vendor, totals, and bank payments).
    """
    list_display = (
        'id',
        'vendor',
        'date_added',
        'payment_type',
        'amount_paid',
        'status',
        'grand_total',
        'tax_amount',
        'amount_change'
    )
    search_fields = ('vendor__name',)
    list_filter = ('payment_type', 'status', 'vendor', 'date_added')
    ordering = ('-date_added',)
    readonly_fields = ('date_added', 'grand_total', 'sub_total', 'tax_amount', 'amount_change')

    def save_model(self, request, obj, form, change):
        """
        Optionally update financial calculations manually here (if not already done in the model).
        """
        obj.grand_total = obj.sub_total + obj.tax_amount
        obj.amount_change = obj.amount_paid - obj.grand_total
        super().save_model(request, obj, form, change)


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    """
    Admin interface for tracking payment records with partial payments across accounts.
    """
    list_display = (
        'id',
        'payment_source_type',
        'get_transaction_id',
        'payment_amount',
        'receiving_bank_account',
        'payment_date'
    )
    search_fields = ('receiving_bank_account__account_name', 'sale__id', 'purchase__id', 'servicebill__id')
    list_filter = ('payment_source_type', 'receiving_bank_account', 'payment_date')
    ordering = ('-payment_date',)
    readonly_fields = ('payment_date',)
    
    def get_transaction_id(self, obj):
        if obj.sale:
            return f"Sale #{obj.sale.id}"
        elif obj.purchase:
            return f"Purchase #{obj.purchase.id}"
        elif obj.servicebill:
            return f"Service #{obj.servicebill.id}"
        return "N/A"
    get_transaction_id.short_description = "Transaction"


        

