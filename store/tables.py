import django_tables2 as tables
from .models import Item, Delivery, catogaryitem


class ItemTable(tables.Table):
    processor = tables.Column(empty_values=(), verbose_name='Processor')
    processor_qty = tables.Column(empty_values=(), verbose_name='Processor_Qty')
    ram = tables.Column(empty_values=(), verbose_name='RAM')
    ram_qty = tables.Column(empty_values=(), verbose_name='Ram_Qty')
    hdd = tables.Column(empty_values=(), verbose_name='HDD')
    hdd_qty = tables.Column(empty_values=(), verbose_name='Hdd_Qty')
    ssd = tables.Column(empty_values=(), verbose_name='SSD')
    ssd_qty = tables.Column(empty_values=(), verbose_name='Ssd_Qty')

    def get_cat_items(self, record):
        return catogaryitem.objects.filter(serial_no=record.serialno)

    def render_processor(self, record):
        items = self.get_cat_items(record).filter(category='processor')
        return ", ".join(f"{item.name} ({item.quantity})" for item in items) if items else "-"

    def render_processor_qty(self, record):
        items = self.get_cat_items(record).filter(category='processor')
        return ", ".join(str(item.quantity) for item in items) if items else "-"

    def render_ram(self, record):
        items = self.get_cat_items(record).filter(category='ram')
        return ", ".join(f"{item.name} ({item.quantity})" for item in items) if items else "-"

    def render_ram_qty(self, record):
        items = self.get_cat_items(record).filter(category='ram')
        return ", ".join(str(item.quantity) for item in items) if items else "-"

    def render_hdd(self, record):
        items = self.get_cat_items(record).filter(category='hdd')
        return ", ".join(f"{item.name} ({item.quantity})" for item in items) if items else "-"

    def render_hdd_qty(self, record):
        items = self.get_cat_items(record).filter(category='hdd')
        return ", ".join(str(item.quantity) for item in items) if items else "-"

    def render_ssd(self, record):
        items = self.get_cat_items(record).filter(category='ssd')
        return ", ".join(f"{item.name} ({item.quantity})" for item in items) if items else "-"

    def render_ssd_qty(self, record):
        items = self.get_cat_items(record).filter(category='ssd')
        return ", ".join(str(item.quantity) for item in items) if items else "-"




    class Meta:
        model = Item
        template_name = "django_tables2/semantic.html"
        fields = (
            'id', 'name', 'serialno', 'make_and_models',
            'processor','processor_qty', 'ram','ram_qty','hdd','hdd_qty','ssd','ssd_qty', 
            'smps_status', 'motherboard_status'
        )
        order_by_field = 'id'


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
