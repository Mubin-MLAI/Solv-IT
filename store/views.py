"""
Module: store.views

Contains Django views for managing items, profiles,
and deliveries in the store application.

Classes handle product listing, creation, updating,
deletion, and delivery management.
The module integrates with Django's authentication
and querying functionalities.
"""

# Standard library imports
import operator
from functools import reduce
from django.contrib import messages
from django.contrib.messages import success

# Django core imports
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum

# Authentication and permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Class-based views
from django.views.generic import (
    DetailView, CreateView, UpdateView, DeleteView, ListView
)
from django.views.generic.edit import FormMixin

# Third-party packages
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from requests import Response

# Local app imports
from accounts.models import Profile, Vendor
from transactions.models import Sale
from .models import  Item, Delivery, Ram, Ssd, Hdd, Processor , catogaryitem  #, Nvme, M_2
from .forms import ItemForm,  DeliveryForm, RamForm, SddForm, HddForm, ProcessorForm , catogaryForm   #, NvmeForm, M_2Form
from .tables import ItemTable, CategoryItemTable
import pandas as pd




@login_required
def dashboard(request):
    user_profile = request.user.profile
    profiles = Profile.objects.all()
    # Category.objects.annotate(nitem=Count("item"))
    # items = Item.objects.all()
    # total_items = (
    #     Item.objects.all()
    #     .aggregate(Sum("quantity"))
    #     .get("quantity__sum", 0.00)
    # )
    # items_count = items.count()
    profiles_count = profiles.count()

    # Prepare data for charts
    # category_counts = Category.objects.annotate(
    #     item_count=Count("item")
    # ).values("name", "item_count")
    # categories = [cat["name"] for cat in category_counts]
    # category_counts = [cat["item_count"] for cat in category_counts]

    sale_dates = (
        Sale.objects.values("date_added__date")
        .annotate(total_sales=Sum("grand_total"))
        .order_by("date_added__date")
    )
    sale_dates_labels = [
        date["date_added__date"].strftime("%Y-%m-%d") for date in sale_dates
    ]
    sale_dates_values = [float(date["total_sales"]) for date in sale_dates]
    

    context = {
        # "items": items,
        "profiles": profiles,
        "profiles_count": profiles_count,
        # "items_count": items_count,
        # "total_items": total_items,
        "vendors": Vendor.objects.all(),
        "delivery": Delivery.objects.all(),
        "sales": Sale.objects.all(),
        # "categories": categories,
        # "category_counts": category_counts,
        "sale_dates_labels": sale_dates_labels,
        "sale_dates_values": sale_dates_values,
        'user_role': user_profile.role,
    }
    print(context)

    if user_profile.role == 'OP':
        return render(request, 'store/operative_dashboard.html')  # A different template for Operative users
    else:
        return render(request, 'store/dashboard.html')
    # return render(request, "store/dashboard.html", context)


class ProductListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to update product information.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - fields: The fields to be updated.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Item
    table_class = ItemTable
    context_object_name = "items"
    paginate_by = 10
    SingleTableView.table_pagination = False

    def get_template_names(self):

        user_profile = self.request.user.profile
        if user_profile.role == 'OP':
            return ["store/operative_dashboard.html"]
        else:
            return ["store/productslist.html"]
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = context['items']  # assuming your ListView or similar sets this

        # Get all category items in one go to reduce DB hits
        all_category_items = catogaryitem.objects.filter(
            serial_no__in=[item.serialno for item in items]
        )

        # Group them by serial number, but only store the component name
        from collections import defaultdict
        grouped_data = defaultdict(lambda: {'processors': [], 'rams': [], 'hdds': [], 'ssds': []})

        for data in all_category_items:
            serial = data.serial_no

            # Store only the component name, not the category
            if data.category == 'processor':
                grouped_data[serial]['processors'].append(data.name + 'X' + '(' + str(data.quantity) + ')' )  # Store only the name
            elif data.category == 'ram':  # Store only the name
                grouped_data[serial]['rams'].append(data.name + 'X' + '(' + str(data.quantity) + ')' )  # Store only the name
            elif data.category == 'hdd':
                grouped_data[serial]['hdds'].append(data.name +'X' + '(' + str(data.quantity) + ')' )  # Store only the name
            elif data.category == 'ssd':
                grouped_data[serial]['ssds'].append(data.name + 'X' + '(' + str(data.quantity) + ')' )  # Store only the name

        # Attach to each item
        for item in items:
            serial = item.serialno
            item.processors = grouped_data[serial]['processors'] 
            item.rams = grouped_data[serial]['rams']
            item.hdds = grouped_data[serial]['hdds']
            item.ssds = grouped_data[serial]['ssds']

        return context


class CatogaryItemListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.

    Attributes:
    - model: The model associated with the view.
    - table_class: The table class used for rendering.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    - paginate_by: Number of items per page for pagination.
    """

    model = catogaryitem
    table_class = CategoryItemTable
    template_name = "store/category_list.html"
    context_object_name = "catogaryitems"
    paginate_by = 10
    SingleTableView.table_pagination = False

class CatogaryItemSearchListView(CatogaryItemListView):
    """
    View class to search and display a filtered list of items.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(CatogaryItemSearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_, (Q(name__icontains=q) | Q(category__icontains=q) | Q(serial_no__icontains=q) for q in query_list)
                )
            )
        return result

class ItemSearchListView(ProductListView):
    """
    View class to search and display a filtered list of items.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(ProductListView, self).get_queryset()

        query = self.request.GET.get("q")

        if not query:
            return result.none()
        
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_, (Q(name__icontains=q) | Q(serialno__icontains=q) | Q(make_and_models__icontains=q) for q in query_list)
                )
            )
        return result
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = context['items']  # assuming your ListView or similar sets this

        # Get all category items in one go to reduce DB hits
        all_category_items = catogaryitem.objects.filter(
            serial_no__in=[item.serialno for item in items]
        )

        # Group them by serial number, but only store the component name
        from collections import defaultdict
        grouped_data = defaultdict(lambda: {'processors': [], 'rams': [], 'hdds': [], 'ssds': []})

        for data in all_category_items:
            serial = data.serial_no
            print('serial', serial)

            # Store only the component name, not the category
            if data.category == 'processor':
                grouped_data[serial]['processors'].append(data.name + 'X' + '(' + str(data.quantity) + ')' )  # Store only the name
            elif data.category == 'ram':  # Store only the name
                grouped_data[serial]['rams'].append(data.name + 'X' + '(' + str(data.quantity) + ')' )  # Store only the name
            elif data.category == 'hdd':
                grouped_data[serial]['hdds'].append(data.name +'X' + '(' + str(data.quantity) + ')' )  # Store only the name
            elif data.category == 'ssd':
                grouped_data[serial]['ssds'].append(data.name + 'X' + '(' + str(data.quantity) + ')' )  # Store only the name

        # Attach to each item
        for item in items:
            serial = item.serialno
            item.processors = grouped_data[serial]['processors'] 
            item.rams = grouped_data[serial]['rams']
            item.hdds = grouped_data[serial]['hdds']
            item.ssds = grouped_data[serial]['ssds']

        return context


class ProductDetailView(LoginRequiredMixin, FormMixin, DetailView):
    """
    View class to display detailed information about a product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    """

    model = Item
    template_name = "store/productdetail.html"

    def get_success_url(self):
        return reverse("product-detail", kwargs={"slug": self.object.slug})


class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    View class to create a new product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - form_class: The form class used for data input.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Item
    template_name = "store/productcreate.html"
    form_class = ItemForm
    success_url = "/products"

    def test_func(self):
        # item = Item.objects.get(id=pk)
        if self.request.POST.get("quantity") < 1:
            return False
        else:
            return True



class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View class to update product information.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - fields: The fields to be updated.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Item
    form_class = ItemForm
    template_name = "store/productupdate.html"  # Default template name
        


    def get_template_names(self):
        user_profile = self.request.user.profile

        # If user is 'OP', change template name to 'operative_productupdate.html'
        if user_profile.role == 'OP':
            return ["store/operative_productupdate.html"]
        else:
            return ["store/productupdate.html"]

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item = self.get_object()  # if it's a DetailView or similar

        # Get all category items for this item’s serial number
        all_category_items = catogaryitem.objects.filter(serial_no__iexact=item.serialno)

        all_category_in_table = catogaryitem.objects.filter(serial_no__iexact = 'Solv-IT').distinct()

        # Filter and format
        processors1 = []
        rams1 = []
        hdds1 = []
        ssds1 = []
        for data in all_category_in_table:
            if data.category == 'processor':
                processors1.append(f"{data.name} X({data.quantity})")
            if data.category == 'ram':
                rams1.append(f"{data.name} X({data.quantity})")
            if data.category == 'hdd':
                hdds1.append(f"{data.name} X({data.quantity})")
            if data.category == 'ssd':
                ssds1.append(f"{data.name} X({data.quantity})")

        context['processor_options1'] = processors1
        context['ram_options1'] = rams1
        context['hdd_options1'] = hdds1
        context['ssd_options1'] = ssds1
        context['item'] = item

        # Filter and format
        processors = []
        rams = []
        hdds = []
        ssds = []
        for data in all_category_items:
            if data.category == 'processor':
                processors.append(f"{data.name} X({data.quantity})")
            if data.category == 'ram':
                rams.append(f"{data.name} X({data.quantity})")
            if data.category == 'hdd':
                hdds.append(f"{data.name} X({data.quantity})")
            if data.category == 'ssd':
                ssds.append(f"{data.name} X({data.quantity})")

        context['processor_options'] = processors
        context['ram_options'] = rams
        context['hdd_options'] = hdds
        context['ssd_options'] = ssds
        context['item'] = item

        return context

    def get_success_url(self):

        """
        Redirect to the products page upon successful form submission.
        """

        if 'button1' in self.request.POST:
            print('button1')
            user_profile = self.request.user.profile
            if user_profile.role == 'OP':
                serialno = self.request.POST['serialno'].strip()
                components = ['ram', 'processor', 'hdd', 'ssd']
                quantities = {
                    'processor': self.request.POST.get('processor_qty', '').strip(),
                    'ram': self.request.POST.get('ram_qty', '').strip(),
                    'hdd': self.request.POST.get('hdd_qty', '').strip(),
                    'ssd': self.request.POST.get('ssd_qty', '').strip(),
                }

                for component in components:
                    print('component',component)
                    item_raw = self.request.POST.get(component, '').strip()
                    if not item_raw:
                        continue

                    qty_raw = quantities[component]
                    qty = int(qty_raw) if qty_raw.isdigit() else 0

                    if qty <= 0:
                        continue

                    clean_name = item_raw.split(' X(')[0].strip()
                    print(f"\nProcessing {component.upper()}: {clean_name} | Qty: {qty}")

                    # Get available item from stock
                    try:
                        available_item = catogaryitem.objects.get(
                            name=clean_name,
                            category=component,
                            serial_no='Solv-IT'
                        )
                    except catogaryitem.DoesNotExist:
                        messages.error(self.request, f"No available '{clean_name}' ({component}) in stock.")
                        return reverse_lazy('dashboard')

                    if available_item.quantity < qty:
                        messages.error(self.request, f"No '{clean_name}' available in {component}.")
                        return reverse_lazy('productslist')

                    # Deduct from stock
                    available_item.quantity -= qty
                    available_item.save()

                    # Assign to serialno: update if exists, else create new
                    assigned_item, created = catogaryitem.objects.get_or_create(
                        name=clean_name,
                        category=component,
                        serial_no=serialno,
                        defaults={
                            'quantity': 0,
                            'unit_price': available_item.unit_price,
                            # add other fields if needed
                        }
                    )

                    assigned_item.quantity += qty
                    assigned_item.save()

                    print(f"✅ Assigned {qty} of '{clean_name}' to {serialno}. {'Created new' if created else 'Updated existing'} entry.")

                messages.success(self.request, "Items assigned successfully.")
                return reverse_lazy('dashboard')
            else:
                messages.success(self.request, "Product update successful!")  # Add a success message
                return reverse_lazy('productslist')
        elif 'button2' in self.request.POST:
            print('button2')
            user_profile = self.request.user.profile
            if user_profile.role == 'OP':
                messages.success(self.request, "Product update successful!")  # Add a success message
                return reverse_lazy('dashboard')
            else:
                messages.success(self.request, "Product update successful!")  # Add a success message
                return reverse_lazy('productslist')
            
        elif 'button3' in self.request.POST:
            print('button del')
            user_profile = self.request.user.profile
            if user_profile.role == 'OP':
                serialno = self.request.POST['serialno'].strip()
                components = ['ram', 'processor', 'hdd', 'ssd']
                quantities = {
                    'processor': self.request.POST.get('processor_qty', '').strip(),
                    'ram': self.request.POST.get('ram_qty', '').strip(),
                    'hdd': self.request.POST.get('hdd_qty', '').strip(),
                    'ssd': self.request.POST.get('ssd_qty', '').strip(),
                }

                for component in components:
                    item_raw = self.request.POST.get(component, '').strip()
                    if not item_raw:
                        continue

                    qty_raw = quantities[component]
                    qty = int(qty_raw) if qty_raw.isdigit() else 0

                    if qty <= 0:
                        continue

                    clean_name = item_raw.split(' X(')[0].strip()
                    print(f"\nProcessing {component.upper()}: {clean_name} | Qty: {qty}")

                    # Get available item from stock
                    try:
                        available_item = catogaryitem.objects.get(
                            name=clean_name,
                            category=component,
                            serial_no=serialno
                        )
                    except catogaryitem.DoesNotExist:
                        messages.error(self.request, f"No available '{clean_name}' ({component}) in stock.")
                        return reverse_lazy('dashboard')

                    if available_item.quantity < qty:
                        messages.error(self.request, f"No '{clean_name}' available in {component}.")
                        return reverse_lazy('productslist')

                    # Deduct from stock
                    available_item.quantity -= qty
                    available_item.save()

                    # Assign to serialno: update if exists, else create new
                    assigned_item, created = catogaryitem.objects.get_or_create(
                        name=clean_name,
                        category=component,
                        serial_no='Solv-IT',
                        defaults={
                            'quantity': 0,
                            'unit_price': available_item.unit_price,
                            # add other fields if needed
                        }
                    )

                    assigned_item.quantity += qty
                    assigned_item.save()

                    print(f"✅ Assigned {qty} of '{clean_name}' to {serialno}. {'Created new' if created else 'Updated existing'} entry.")

                messages.success(self.request, "Product Move to Solv-IT DB!")
                return reverse_lazy('dashboard')
            else:
                messages.success(self.request, "Product update successful!")  # Add a success message
                return reverse_lazy('productslist')
        else:
            print('button3')
            user_profile = self.request.user.profile
            if user_profile.role == 'OP':
                messages.success(self.request, "Product update successful!")  # Add a success message
                return reverse_lazy('dashboard')
            else:
                serialno = self.request.POST['serialno'].strip()

                components = ['processor', 'ram', 'hdd', 'ssd']
                for component in components:
                    component_id = self.request.POST[f'{component}s'].strip()  # e.g., 'processors', 'rams', etc.
                    source_items = catogaryitem.objects.filter(serial_no=serialno, category=component)
                    target_items = catogaryitem.objects.filter(id=component_id, category=component)
                    print(f'{component} serialno:', serialno)
                    for source, target in zip(source_items, target_items):
                        print('post data', source.name, target.name)
                        target.serial_no = source.serial_no
                        target.save()
                        source.serial_no = 'Solv-IT'
                        source.save()

                messages.success(self.request, "Product update successful!")  # Add a success message
                return reverse_lazy('productslist')
    


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View class to delete a product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Item
    template_name = "store/productdelete.html"
    success_url = "/products"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


class DeliveryListView(
    LoginRequiredMixin, ExportMixin, tables.SingleTableView
):
    """
    View class to display a list of deliveries.

    Attributes:
    - model: The model associated with the view.
    - pagination: Number of items per page for pagination.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    """

    model = Delivery
    pagination = 10
    template_name = "store/deliveries.html"
    context_object_name = "deliveries"


class DeliverySearchListView(DeliveryListView):
    """
    View class to search and display a filtered list of deliveries.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(DeliverySearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.
                    and_, (Q(customer_name__icontains=q) for q in query_list)
                )
            )
        return result


class DeliveryDetailView(LoginRequiredMixin, DetailView):
    """
    View class to display detailed information about a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    """

    model = Delivery
    template_name = "store/deliverydetail.html"


class DeliveryCreateView(LoginRequiredMixin, CreateView):
    """
    View class to create a new delivery.

    Attributes:
    - model: The model associated with the view.
    - fields: The fields to be included in the form.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries"


class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
    """
    View class to update delivery information.

    Attributes:
    - model: The model associated with the view.
    - fields: The fields to be updated.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries"


class DeliveryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View class to delete a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Delivery
    template_name = "store/productdelete.html"
    success_url = "/deliveries"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


class CategoryListView(LoginRequiredMixin, ListView):
    model = catogaryitem
    template_name = 'store/category_list.html'
    context_object_name = 'Category'
    paginate_by = 10
    login_url = 'login'

class HddCategoryListView(LoginRequiredMixin, ListView):
    model = Hdd
    template_name = 'store/category_list_hdd.html'
    context_object_name = 'Hdd'
    paginate_by = 10
    login_url = 'login'
    


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = catogaryitem
    template_name = 'store/category_detail.html'
    context_object_name = 'category'
    login_url = 'login'

class HddCategoryDetailView(LoginRequiredMixin, DetailView):
    model = Hdd
    template_name = 'store/category_detail.html'
    context_object_name = 'category'
    login_url = 'login'



class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = catogaryitem
    template_name = 'store/category_form.html'
    form_class = catogaryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class HddCategoryCreateView(LoginRequiredMixin, CreateView):
    model = Hdd
    template_name = 'store/category_list_hdd.html'
    form_class = HddForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = catogaryitem
    template_name = 'store/category_form.html'
    form_class = catogaryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})

class HddCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Hdd
    template_name = 'store/category_form.html'
    form_class = HddForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail-hdd', kwargs={'pk': self.object.pk})


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Ram
    template_name = 'store/category_confirm_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category-list')
    login_url = 'login'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@csrf_exempt
@require_POST
@login_required

def get_items_ajax_view(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Fix is_ajax() issue
        try:
            term = request.POST.get("term", "").strip()
            print("POST Data:", request.POST)  # Debugging
            print("Search Term:", term)

            if not term:
                return JsonResponse({'error': 'No search term provided'}, status=400)

            # items = Item.objects.filter(make_and_models__icontains=term)
            items = catogaryitem.objects.filter(name__icontains=term)
            
            data = [{'id': item.id, 'name': item.name, 'price': item.unit_price, 'total_item': item.unit_price + item.quantity} for item in items[:10]]  # Fix .to_json()
            
            print("Filtered Data:", data)  # Debugging
            return JsonResponse(data, safe=False)

        except Exception as e:
            print("Error:", str(e))  # Debugging
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Not an AJAX request'}, status=400)




from django.http import JsonResponse
from .models import Item  # Replace with your model


def search_suggestions(request):
    query = request.GET.get('q', '')
    items = catogaryitem.objects.all()  # Start by getting all items
    suggestions = []

    if query:
        # Filter items based on the query's initial letters
        items = catogaryitem.objects.filter(name__icontains=query)  # or filter based on other fields as needed
        item1 = catogaryitem.objects.filter(serial_no__icontains=query)
        item2 = catogaryitem.objects.filter(category__icontains=query)
        if items:
            suggestions = list(set([f"{item.name}" for item in items]))
        elif item1:
            suggestions = list(set([f"{item.serial_no}" for item in item1]))
        else:
            suggestions = list(set([f"{item.category}" for item in item2])) # or other fields like item.serial_no, etc.
    return JsonResponse({'suggestions': suggestions})
    
def search_suggestions_product(request):
    query = request.GET.get('q', '')
    items = Item.objects.all()  # Start by getting all items
    suggestions = []
    
    if query:
        # Filter items based on the query's initial letters
        items = Item.objects.filter(name__icontains=query)  # or filter based on other fields as needed
        item1 = Item.objects.filter(serialno__icontains=query)
        item2 = Item.objects.filter(make_and_models__icontains=query)
        if items:
            suggestions = list(set([f"{item.name}" for item in items]))
        elif item1:
            suggestions = list(set([f"{item.serialno}" for item in item1]))
        else:
            suggestions = list(set([f"{item.make_and_models}" for item in item2])) # or other fields like item.serial_no, etc.
    return JsonResponse({'suggestions': suggestions})


from django.shortcuts import render
from django.http import JsonResponse
from .forms import ProcessorForm, HddForm, SddForm

def add_processor1(request):
    serialno = request.GET.get('serialno', '')
    if serialno:
        processors = Processor.objects.filter(serial_no=serialno)
        processor_list = [{"id": processor.id, "name": processor.name} for processor in processors]
        return JsonResponse({"processors": processor_list, 'success': True})
    return JsonResponse({"processors": [], 'success': False})

# View for adding a new Processor
def add_processor(request):
    if request.method == 'POST' and request.is_ajax():
        form = ProcessorForm(request.POST)
        if form.is_valid():
            processor = form.save()
            return JsonResponse({'success': True, 'id': processor.id, 'name': processor.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# View for adding a new HDD
def add_hdd(request):
    if request.method == 'POST' and request.is_ajax():
        form = HddForm(request.POST)
        if form.is_valid():
            hdd = form.save()
            return JsonResponse({'success': True, 'id': hdd.id, 'name': hdd.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        
# View for adding a new HDD
def add_ram(request):
    if request.method == 'POST' and request.is_ajax():
        form = RamForm(request.POST)
        if form.is_valid():
            ram = form.save()
            return JsonResponse({'success': True, 'id': ram.id, 'name': ram.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

# View for adding a new SSD
def add_ssd(request):
    if request.method == 'POST' and request.is_ajax():
        form = SddForm(request.POST)
        if form.is_valid():
            ssd = form.save()
            return JsonResponse({'success': True, 'id': ssd.id, 'name': ssd.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        

@csrf_exempt  # or use @csrf_protect and ensure CSRF is handled via token
def create_processor(request):
    if request.method == 'POST':
        form = ProcessorForm(request.POST)
        if form.is_valid():
            processor = form.save()
            return JsonResponse({
                'success': True,
                'processor': {
                    'id': processor.id,
                    'name': processor.name
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        


def get_category_items(request):
    serial = request.GET.get("serial", "")
    data = {
        "processors": list(catogaryitem.objects.filter(category='processor', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
        "rams": list(catogaryitem.objects.filter(category='ram', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
        "hdds": list(catogaryitem.objects.filter(category='hdd', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
        "ssds": list(catogaryitem.objects.filter(category='ssd', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
    }
    return JsonResponse(data)


def operativedashboard(request):
    user_profile = request.user.profile
    if user_profile.role == 'OP':
        return render(request, "store/operative_productupdate.html")
    else:
        return render(request, "store/productslist.html")
        



