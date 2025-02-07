import django_tables2 as tables
from .models import Item, Delivery, catogaryitem


class ItemTable(tables.Table):
    """
    Table representation for Item model.
    """
    class Meta:
        model = Item
        template_name = "django_tables2/semantic.html"
        fields = (
            'id', 'name', 'serialno', 'make_and_models', 
            'processor', 'ram', 'hdd',
            'ssd', 'smps_status', 'motherboard_status'
        )
        order_by_field = 'id'  # or any other field you prefer

class CategoryItemTable(tables.Table):
    """
    Table representation for CategoryItem model.
    """
    category = tables.Column(verbose_name='Category')
    name = tables.Column(verbose_name='Name')
    serial_no = tables.Column(verbose_name='Serial Number')
    quantity = tables.Column(verbose_name='Quantity')
    unit_price = tables.Column(verbose_name='Unit Price')

    class Meta:
        model = catogaryitem  # Change model to CategoryItem
        template_name = "django_tables2/semantic.html"  # You can use any template you like
        fields = ('category', 'name', 'serial_no', 'quantity', 'unit_price')  # The fields to be displayed in the table
        order_by_field = 'id'  # Default ordering can be set to ID or any other field as needed


class DeliveryTable(tables.Table):
    """
    Table representation for Delivery model.
    """
    class Meta:
        model = Delivery
        fields = (
            'id', 'item', 'customer_name', 'phone_number',
            'location', 'date', 'is_delivered'
        )
