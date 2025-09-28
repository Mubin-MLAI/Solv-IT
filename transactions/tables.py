import django_tables2 as tables
from .models import Sale, Purchase, Bankaccount, catogaryitempurchased, Itempurchased
from store.models import catogaryitem, Item


class PurchasedItemTable(tables.Table):
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
        return ", ".join(f"{item.name}" for item in items) if items else "-"

    def render_processor_qty(self, record):
        items = self.get_cat_items(record).filter(category='processor')
        return ", ".join(str(item.quantity) for item in items) if items else "-"

    def render_ram(self, record):
        items = self.get_cat_items(record).filter(category='ram')
        return ", ".join(f"{item.name}" for item in items) if items else "-"

    def render_ram_qty(self, record):
        items = self.get_cat_items(record).filter(category='ram')
        return ", ".join(str(item.quantity) for item in items) if items else "-"

    def render_hdd(self, record):
        items = self.get_cat_items(record).filter(category='hdd')
        return ", ".join(f"{item.name}" for item in items) if items else "-"

    def render_hdd_qty(self, record):
        items = self.get_cat_items(record).filter(category='hdd')
        return ", ".join(str(item.quantity) for item in items) if items else "-"

    def render_ssd(self, record):
        items = self.get_cat_items(record).filter(category='ssd')
        return ", ".join(f"{item.name}" for item in items) if items else "-"

    def render_ssd_qty(self, record):
        items = self.get_cat_items(record).filter(category='ssd')
        return ", ".join(str(item.quantity) for item in items) if items else "-"




    class Meta:
        model = Item
        template_name = "django_tables2/semantic.html"
        fields = (
            'id', 'name','customer','purchased_code','created_date','price', 'serialno', 'make_and_models',
            'processor','processor_qty', 'ram','ram_qty','hdd','hdd_qty','ssd','ssd_qty','smps_status', 'motherboard_status'
        )
        order_by_field = 'id'


class SaleTable(tables.Table):
    class Meta:
        model = Sale
        template_name = "django_tables2/semantic.html"
        fields = (
            'item',
            'customer_name',
            'transaction_date',
            'payment_method',
            'quantity',
            'price',
            'total_value',
            'amount_received',
            'balance',
            'profile'
        )
        order_by_field = 'sort'


class PurchaseTable(tables.Table):
    class Meta:
        model = Purchase
        template_name = "django_tables2/semantic.html"
        fields = (
            'item',
            'vendor',
            'order_date',
            'delivery_date',
            'quantity',
            'delivery_status',
            'price',
            'total_value'
        )
        order_by_field = 'sort'


class BankTable(tables.Table):
    class Meta:
        model = Bankaccount
        template_name = "django_tables2/semantic.html"
        fields = (
            'account_name',
            'opening_balance',
            'as_of_date'
        )
        order_by_field = 'id'
