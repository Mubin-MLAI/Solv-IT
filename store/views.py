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
from collections import defaultdict
from itertools import zip_longest
import operator
from functools import reduce
import re
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
from django.utils import timezone

# Third-party packages
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from requests import Response

# Local app imports
from accounts.models import Profile, Vendor
from transactions.models import Itempurchased, Sale, catogaryitempurchased
from .models import  Item, Delivery, Ram, Ssd, Hdd, Processor , catogaryitem  #, Nvme, M_2
from .forms import ItemForm,  DeliveryForm, RamForm, SddForm, HddForm, ProcessorForm , catogaryForm   #, NvmeForm, M_2Form
from .tables import ItemTable, CategoryItemTable
from accounts.models import Customer
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["POST"])
def create_customer_ajax(request):
    try:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        
        if not first_name or not phone:
            return JsonResponse({
                'success': False,
                'error': 'First name and phone number are required'
            })
            
        # Create new customer
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name or '',
            phone=phone
        )
        
        # Return success response with customer data
        return JsonResponse({
            'success': True,
            'customer': {
                'id': customer.id,
                'full_name': f"{customer.first_name} {customer.last_name}".strip(),
                'phone': customer.phone
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
import pandas as pd
from django.db import transaction
from .forms import ExcelUploadForm
from django.db.models import Min




@login_required
def dashboard(request):
    # Solv-IT stock by category
    stock_categories = ['ssd', 'processor', 'hdd', 'ram']
    stock_summary = {}
    for cat in stock_categories:
        qty = catogaryitem.objects.filter(category=cat, serial_no__iexact='Solv-IT').aggregate(total=Sum('quantity'))['total'] or 0
        stock_summary[cat] = qty
    user_profile = request.user.profile
    profiles = Profile.objects.all()
    profiles_count = profiles.count()
    customers_count = Customer.objects.count()
    # Total inventory quantity (sum of all Item.quantity)
    total_items = Item.objects.aggregate(total=Sum('quantity'))['total'] or 0

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
        "profiles": profiles,
        "profiles_count": profiles_count,
        "customers_count": customers_count,
        "total_items": total_items,
        "vendors": Vendor.objects.all(),
        "delivery": Delivery.objects.all(),
        "sales": Sale.objects.all(),
        "sale_dates_labels": sale_dates_labels,
        "sale_dates_values": sale_dates_values,
        'user_role': user_profile.role,
        'stock_summary': stock_summary,
    }

    if user_profile.role == 'OP':
        return render(request, 'store/operative_dashboard.html', context)  # A different template for Operative users
    else:
        return render(request, 'store/dashboard.html', context)


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


        print('working ')
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
    model = catogaryitem
    table_class = CategoryItemTable
    template_name = "store/category_list.html"
    context_object_name = "catogaryitems"
    paginate_by = 10
    SingleTableView.table_pagination = False

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
    

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class ItemSearchListView(ProductListView):
    """
    View class to search and display a filtered list of items.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """
    table_class = ItemTable
    paginate_by = 10
    SingleTableView.table_pagination = False

    def get_queryset(self):
        result = super().get_queryset()

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
    


from django.http import JsonResponse
from .models import Customer

def customer_search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query and len(query) >= 2:
        print('Query:', query)  # Debugging line
        customers = Customer.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(phone__icontains=query)
        )[:10]
        suggestions = [
            {
                'id': customer.pk,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'text': (customer.first_name + ' ' + customer.last_name).strip() if customer.last_name else customer.first_name
            }
            for customer in customers
        ]

    return JsonResponse({'results': suggestions})




from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Customer, catogaryitem  # make sure to import Customer

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = "store/productcreate.html"
    form_class = ItemForm

    def form_valid(self, form):
        item = form.save(commit=False)
        item.created_by = self.request.user  # Set the user who created the item

        # ✅ Get the customer ID from the POST data
        customer_id = self.request.POST.get('customer_id')
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                item.customer = customer  # Assuming Item has a ForeignKey to Customer
            except Customer.DoesNotExist:
                messages.error(self.request, "Selected customer does not exist.")
                return self.form_invalid(form)

        item.save()

        serialno = item.serialno.strip()
        component_fields = ['processor', 'ram', 'hdd', 'ssd']

        try:
            for component in component_fields:
                names_str = self.request.POST.get(component, '')
                qtys_str = self.request.POST.get(f"{component}_qty", '')

                names = [name.strip() for name in names_str.split(',') if name.strip()]
                qtys = [qty.strip() for qty in qtys_str.split(',') if qty.strip()]

                if len(names) != len(qtys):
                    messages.error(self.request, f"Mismatch in count of names and quantities for {component}.")
                    continue

                for name, qty in zip(names, qtys):
                    try:
                        qty_int = int(qty)
                        if qty_int <= 0:
                            continue
                    except ValueError:
                        messages.error(self.request, f"Invalid quantity '{qty}' for {component} '{name}'")
                        continue

                    catogaryitem.objects.create(
                        name=name.upper(),
                        category=component,
                        serial_no=serialno,
                        quantity=qty_int,
                        unit_price=0.00,
                        created_by=self.request.user
                    )
        except Exception as e:
            messages.error(self.request, f"Error while saving components: {str(e)}")

        messages.success(self.request, "Product and components saved.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('productslist')



def ordinal(n):
    return f"{n}{'th' if 11 <= n <= 14 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"



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

    def form_invalid(self, form):
        print("FORM INVALID:", form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # Extract raw strings from POST
        print("FORM ERRORS:", form.errors)
        ram_names = self.request.POST.get("ram", "")
        ram_qtys = self.request.POST.get("ram_qty", "")
        
        # Split by comma and strip spaces
        ram_name_list = [name.strip() for name in ram_names.split(",") if name.strip()]
        ram_qty_list = [qty.strip() for qty in ram_qtys.split(",") if qty.strip()]
        
        # Validate: names and quantities count must match
        if len(ram_name_list) != len(ram_qty_list):
            form.add_error(None, "RAM names and quantities must match.")
            return self.form_invalid(form)
        
        # Convert qty to integers and combine
        ram_items = []
        try:
            for name, qty in zip(ram_name_list, ram_qty_list):
                ram_items.append({
                    "name": name,
                    "qty": int(qty)
                })
        except ValueError:
            form.add_error(None, "Quantities must be valid integers.")
            return self.form_invalid(form)

        # Example: Save to DB or process
        print("RAM Items:", ram_items)

        # Repeat similar parsing for processor, hdd, ssd if needed
        return super().form_valid(form)


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
        all_category_items = catogaryitem.objects.filter(serial_no__iexact='Solv-IT', quantity__gt=0)
        operative_page_item = catogaryitem.objects.filter(serial_no__iexact=item.serialno)
        
        


        all_category_in_table = catogaryitem.objects.filter(serial_no__iexact='Solv-IT', quantity__gt=0).distinct()

        # Prepare processor-by-generation buckets (1st Generation .. 13th Generation) and Unknown
        processor_by_generation = {f"{ordinal(i)} Generation": [] for i in range(1, 20)}
        processor_by_generation['Unknown'] = []

        # A separate dict for consolidated results
        processor_by_generation1 = {f"{ordinal(i)} Generation": [] for i in range(1, 20)}
        processor_by_generation1['Unknown'] = []

        # ------------------- Processor: Group by Generation -------------------
        for data in all_category_in_table:
            if data.category == 'processor':
                match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s*(?:Gen|Generation)', data.name, re.IGNORECASE)
                if match:
                    gen_number = int(match.group(1))
                    generation_label = f"{ordinal(gen_number)} Generation"
                    if generation_label in processor_by_generation:
                        processor_by_generation[generation_label].append(f"{data.name} X({data.quantity}) - ({data.serial_no})")
                    else:
                        # Add to Unknown bucket
                        processor_by_generation['Unknown'].append(f"{data.name} X({data.quantity}) - ({data.serial_no})")
                else:
                    processor_by_generation['Unknown'].append(f"{data.name} X({data.quantity}) - ({data.serial_no})")

        # Consolidate processor entries with the same name and serial_no
        for generation, options in processor_by_generation.items():
            # Consolidate entries with the same name and serial_no
            consolidated = {}
            for option in options:
                if not option:  # Skip empty entries
                    continue
                    
                # Parse the option string to extract parts
                name_parts = option.split(" X(")
                if len(name_parts) < 2:  # Skip malformed entries
                    continue
                    
                item_name = name_parts[0]
                qty_serial = name_parts[1]
                
                try:
                    qty = int(qty_serial.split(")")[0])
                    serial_no = qty_serial.split("- (")[1].rstrip(")")
                    
                    # Create a key for consolidation
                    key = (item_name, serial_no)
                    
                    # Add to consolidated dict
                    if key not in consolidated:
                        consolidated[key] = {'name': item_name, 'qty': qty, 'serial_no': serial_no}
                    else:
                        consolidated[key]['qty'] += qty
                except (IndexError, ValueError):
                    # Skip entries that don't match expected format
                    continue
            
            # Rebuild the options list with consolidated items
            processor_by_generation1[generation] = [
                f"{item['name']} X({item['qty']}) - ({item['serial_no']})" 
                for item in consolidated.values()
            ]
            
        for generation, options in processor_by_generation1.items():
            print('processor_by_generation', generation, options)

        
        
        # ------------------- RAM, HDD, SSD: Group by Size -------------------
        hdd_sizes = [
            '40GB', '80GB', '120GB', '160GB', '250GB', '320GB', '500GB', '640GB',
            '750GB', '1TB', '1.5TB', '2TB', '3TB', '4TB', '5TB', '6TB', '8TB',
            '10TB', '12TB', '14TB', '16TB', '18TB', '20TB'
        ]

        ssd_sizes = [
            '64GB', '120GB','140GB' ,'128GB', '240GB', '250GB', '256GB', '480GB', '500GB',
            '512GB', '1TB', '2TB', '4TB', '8TB'
        ]

        ram_sizes = [
            '2GB', '4GB', '6GB', '8GB', '12GB', '16GB', '24GB', '32GB', '48GB',
            '64GB', '96GB', '128GB'
        ]

        rambysize = {}
        rambysize1 = {}
        hddbysize = {}
        ssdbysize = {}


        for data in all_category_in_table:
            if data.category == 'ram':
                ram_name = data.name.strip()
                
                # Try to extract the RAM size from the name
                size_found = next((size for size in ram_sizes if size in ram_name), None)
                
                # Determine the size label or use 'Unknown'
                size_key = size_found if size_found else 'Unknown'
                
                # Initialize the key in dict if not present
                if size_key not in rambysize:
                    rambysize[size_key] = []

                # Add the formatted RAM info
                rambysize[size_key].append(f"{ram_name} X({data.quantity}) - ({data.serial_no})")
                for size, options in rambysize.items():
                    # Consolidate entries with the same name and serial_no
                    consolidated = {}
                    for option in options:
                        # Parse the option string to extract parts
                        name_parts = option.split(" X(")
                        item_name = name_parts[0]
                        qty_serial = name_parts[1]
                        qty = int(qty_serial.split(")")[0])
                        serial_no = qty_serial.split("- (")[1].rstrip(")")
                        
                        # Create a key for consolidation
                        key = (item_name, serial_no)
                        
                        # Add to consolidated dict
                        if key not in consolidated:
                            consolidated[key] = {'name': item_name, 'qty': qty, 'serial_no': serial_no}
                        else:
                            consolidated[key]['qty'] += qty
                    
                    # Rebuild the options list with consolidated items
                    rambysize1[size] = [f"{item['name']} X({item['qty']}) - ({item['serial_no']})" 
                                    for item in consolidated.values()]
                    
                # print('rambysize', ram_size, rambysize1[size])
                
            elif data.category == 'hdd':
                hdd_name = data.name.strip()
                
                # Try to extract the HDD size from the name
                size_found = next((size for size in hdd_sizes if size in hdd_name), None)
                
                # Determine the size label or use 'Unknown'
                size_key = size_found if size_found else 'Unknown'
                
                # Initialize the key in dict if not present
                if size_key not in hddbysize:
                    hddbysize[size_key] = []

                # Add the formatted HDD info
                hddbysize[size_key].append(f"{hdd_name} X({data.quantity}) - ({data.serial_no})")

            elif data.category == 'ssd':
                ssd_name = data.name.strip()
                
                # Try to extract the SSD size from the name
                size_found = next((size for size in ssd_sizes if size in ssd_name), None)
                
                # Determine the size label or use 'Unknown'
                size_key = size_found if size_found else 'Unknown'
                
                # Initialize the key in dict if not present
                if size_key not in ssdbysize:
                    ssdbysize[size_key] = []

                # Add the formatted SSD info
                ssdbysize[size_key].append(f"{ssd_name} X({data.quantity}) - ({data.serial_no})")

        # Output the structure
        # Consolidate HDD entries
        hddbysize1 = {}
        for size, options in hddbysize.items():
            # Consolidate entries with the same name and serial_no
            consolidated = {}
            for option in options:
                if not option:  # Skip empty entries
                    continue
                
                # Parse the option string to extract parts
                name_parts = option.split(" X(")
                if len(name_parts) < 2:  # Skip malformed entries
                    continue
                    
                item_name = name_parts[0]
                qty_serial = name_parts[1]
                
                try:
                    qty = int(qty_serial.split(")")[0])
                    serial_no = qty_serial.split("- (")[1].rstrip(")")
                    
                    # Create a key for consolidation
                    key = (item_name, serial_no)
                    
                    # Add to consolidated dict
                    if key not in consolidated:
                        consolidated[key] = {'name': item_name, 'qty': qty, 'serial_no': serial_no}
                    else:
                        consolidated[key]['qty'] += qty
                except (IndexError, ValueError):
                    # Skip entries that don't match expected format
                    continue
            
            # Rebuild the options list with consolidated items
            hddbysize1[size] = [
                f"{item['name']} X({item['qty']}) - ({item['serial_no']})" 
                for item in consolidated.values()
            ]
        
        # Consolidate SSD entries
        ssdbysize1 = {}
        for size, options in ssdbysize.items():
            # Consolidate entries with the same name and serial_no
            consolidated = {}
            for option in options:
                if not option:  # Skip empty entries
                    continue
                
                # Parse the option string to extract parts
                name_parts = option.split(" X(")
                if len(name_parts) < 2:  # Skip malformed entries
                    continue
                    
                item_name = name_parts[0]
                qty_serial = name_parts[1]
                
                try:
                    qty = int(qty_serial.split(")")[0])
                    serial_no = qty_serial.split("- (")[1].rstrip(")")
                    
                    # Create a key for consolidation
                    key = (item_name, serial_no)
                    
                    # Add to consolidated dict
                    if key not in consolidated:
                        consolidated[key] = {'name': item_name, 'qty': qty, 'serial_no': serial_no}
                    else:
                        consolidated[key]['qty'] += qty
                except (IndexError, ValueError):
                    # Skip entries that don't match expected format
                    continue
            
            # Rebuild the options list with consolidated items
            ssdbysize1[size] = [
                f"{item['name']} X({item['qty']}) - ({item['serial_no']})" 
                for item in consolidated.values()
            ]

        # Add to context with consolidated data
        context['processor_by_generation'] = processor_by_generation1
        context['rambysize'] = rambysize1
        context['hddbysize'] = hddbysize1
        context['ssdbysize'] = ssdbysize1
        context['item'] = item

        #-------------------For Display all Material in Solv-IT DB in OP Form--------------------

        # Filter and format
        processors = []
        rams = []
        hdds = []
        ssds = []
        for data in all_category_items:
            if data.category == 'processor':
                processors.append(f"{data.name} X({data.quantity}) --({data.serial_no})")
            if data.category == 'ram':
                rams.append(f"{data.name} X({data.quantity}) --({data.serial_no})")
            if data.category == 'hdd':
                hdds.append(f"{data.name} X({data.quantity}) --({data.serial_no})")
            if data.category == 'ssd':
                ssds.append(f"{data.name} X({data.quantity}) --({data.serial_no})")

        context['processor_options'] = processors
        context['ram_options'] = rams
        context['hdd_options'] = hdds
        context['ssd_options'] = ssds
        context['item'] = item
        

        #-------------------For Move / Remove product to Solv-IT DB--------------------
        # Filter and format
        processor2 = []
        ram2 = []
        hdd2 = []
        ssd2 = []
        for data in operative_page_item:
            if data.category == 'processor':
                processor2.append(f"{data.name} X({data.quantity})")
            if data.category == 'ram':
                ram2.append(f"{data.name} X({data.quantity})")
            if data.category == 'hdd':
                hdd2.append(f"{data.name} X({data.quantity})")
            if data.category == 'ssd':
                ssd2.append(f"{data.name} X({data.quantity})")

        context['processor_option2'] = processor2
        context['ram_option2'] = ram2
        context['hdd_option2'] = hdd2
        context['ssd_option2'] = ssd2
        context['item'] = item

        #--------------------------FOR Main Form Update-----------------------------------
        processor_names = []
        processor_qty = []
        ram_names = []
        ram_qty = []
        hdd_names = []
        hdd_qty = []
        ssd_names = []
        ssd_qty = []

        for data in operative_page_item:
            if data.category == 'processor':
                processor_names.append(data.name)
                processor_qty.append(data.quantity)
            elif data.category == 'ram':
                ram_names.append(data.name)
                ram_qty.append(data.quantity)
            elif data.category == 'hdd':
                hdd_names.append(data.name)
                hdd_qty.append(data.quantity)
            elif data.category == 'ssd':
                ssd_names.append(data.name)
                ssd_qty.append(data.quantity)
        # Add to context
        context['processor_option3'] = processor_names
        context['processor_qty3'] = processor_qty
        context['ram_option3'] = ram_names
        context['ram_qty3'] = ram_qty
        context['hdd_option3'] = hdd_names
        context['hdd_qty3'] = hdd_qty
        context['ssd_option3'] = ssd_names
        context['ssd_qty3'] = ssd_qty
        context['item'] = item


        return context

    def get_success_url(self):

        """
        Redirect to the products page upon successful form submission.
        """
        print('success function')

        if 'button1' in self.request.POST:
            print(self.request.POST)
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
                    
                    qty2 = qty

                    # Get all matching items and work with total available quantity
                    available_items = catogaryitem.objects.filter(
                        name=clean_name,
                        category=component,
                        serial_no='Solv-IT'
                    )

                    if not available_items.exists():
                        messages.error(self.request, f"No available '{clean_name}' ({component}) in stock.")
                        return reverse_lazy('dashboard')

                    total_available = sum(item.quantity for item in available_items)
                    if total_available < qty:
                        messages.error(self.request, f"Not enough '{clean_name}' available in {component}.")
                        return reverse_lazy('productslist')

                    # Get the unit price from the first item (assuming all have the same price)
                    # unit_price = available_items.first().unit_price
                    # print('unit_price', unit_price)

                    
                    # ✅ Get the minimum unit price from available items
                    unit_price = available_items.aggregate(Min('unit_price'))['unit_price__min']
                    print('unit_price', unit_price)

                    # Addition of price based on category price on purchased price
                    update_items = Item.objects.filter(serialno__iexact=serialno)
                    for items1 in update_items:
                        print('items1', items1, items1.price)
                        items1.price += unit_price
                        items1.save()

                    # Deduct from items (FIFO approach)
                    remaining_to_deduct = qty
                    for item in available_items:
                        if remaining_to_deduct <= 0:
                            break
                            
                        deduct_amount = min(item.quantity, remaining_to_deduct)
                        item.quantity -= deduct_amount
                        remaining_to_deduct -= deduct_amount
                        
                        if item.quantity <= 0:
                            item.delete()
                        else:
                            item.save()

                    # Assign to serialno: update if exists, else create new
                    assigned_item, created = catogaryitem.objects.get_or_create(
                        name=clean_name,
                        category=component,
                        serial_no=serialno,
                        updated_by=self.request.user,
                        defaults={
                            'quantity': 0,
                            'unit_price': unit_price,  # Now using unit_price from first item
                            # add other fields if needed
                        }
                    )

                    assigned_item.quantity += qty
                    assigned_item.updated_by = self.request.user
                    assigned_item.save()    

                    # print("✅ Assigned {} of '{}' to {}. {} entry.".format(qty, clean_name, serialno, 'Created new' if created else 'Updated existing'))

                messages.success(self.request, "✅ Assigned {} of '{}' to {}. {} entry.".format(qty2, clean_name, serialno, 'Created new' if created else 'Updated existing'))
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
                components = ['processor','ram', 'hdd', 'ssd']
                quantities = {
                    'processor': self.request.POST.get('processor_qty', '').strip(),
                    'ram': self.request.POST.get('ram_qty', '').strip(),
                    'hdd': self.request.POST.get('hdd_qty', '').strip(),
                    'ssd': self.request.POST.get('ssd_qty', '').strip(),
                }

                for component in components:
                    print('component', self.request.POST.get(component, '').strip())
                    item_raw = self.request.POST.get(component, '').strip()
                    print('item_raw', item_raw)
                    if not item_raw:
                        continue

                    qty_raw = quantities[component]
                    qty = int(qty_raw) if qty_raw.isdigit() else 0

                    if qty <= 0:
                        continue

                    clean_name = item_raw.split(' X(')[0].strip()
                    print(f"\nProcessing {component.upper()}: {clean_name} | Qty: {qty}")

                    # Get the item from the source device (e.g., LAP786786)
                    # try:
                    assigned_item = catogaryitem.objects.filter(
                        name=clean_name,
                        category=component,
                        serial_no=serialno
                    )
                    # except catogaryitem.DoesNotExist:
                    #     messages.error(self.request, "No '{}' assigned to {}.".format(clean_name, serialno))
                    #     return reverse_lazy('productslist')

                    total_available = sum(item.quantity for item in assigned_item)
                    if total_available < qty:
                        messages.error(self.request, "Not enough '{}' in {}.".format(clean_name, serialno))
                        return reverse_lazy('productslist')
                    

                    # ✅ Get the minimum unit price from available items
                    unit_price = assigned_item.aggregate(Min('unit_price'))['unit_price__min']
                    print('unit_price', unit_price)

                    # Addition of price based on category price on purchased price
                    update_items = Item.objects.filter(serialno__iexact=serialno)
                    for items1 in update_items:
                        print('items1', items1, items1.price)
                        items1.price -= unit_price
                        items1.save()

                    # Deduct from source
                    total_available -= qty
                    
                    if total_available <= 0:
                        assigned_item.delete()
                        # print("❌ Deleted {} from {} (Qty reached zero).".format(clean_name, serialno))
                    else:
                        assigned_item.updated_by = self.request.user
                        assigned_item.save()
                        # print("➖ Deducted {} from {} ({}). Remaining: {}".format(qty, serialno, clean_name, assigned_item.quantity))

                    # Add to 'Solv-IT'
                    stock_item, created = catogaryitem.objects.get_or_create(
                        name=clean_name,
                        category=component,
                        serial_no='Solv-IT',
                        updated_by = self.request.user,
                        defaults={
                            'quantity': 0,
                            'unit_price': sum(item.unit_price for item in assigned_item) / len(assigned_item) if assigned_item else 0,
                        }
                    )
                    stock_item.quantity += qty
                    stock_item.updated_by = self.request.user
                    stock_item.save()

                    # print("✅ Moved {} of '{}' to Solv-IT. {} entry.".format(qty, clean_name, 'Created new' if created else 'Updated existing'))


                messages.success(self.request, "✅ Moved {} of '{}' to Solv-IT. {} entry.".format(qty, clean_name, 'Created new' if created else 'Updated existing'))
                return reverse_lazy('dashboard')
            else:
                messages.success(self.request, "Product update successful!")  # Add a success message
                return reverse_lazy('productslist')
        else:
            serialno = self.request.POST['serialno'].strip()
            print('serialno', serialno)
            print('dataaa', self.request.POST)

            components = ['processor', 'ram', 'hdd', 'ssd']
            print('processor data',self.request.POST.get('processor', '').strip())

            # Get quantities from POST data
            quantities = {
                'processor': self.request.POST.get('processor_qty', '').strip(),
                'ram': self.request.POST.get('ram_qty', '').strip(),
                'hdd': self.request.POST.get('hdd_qty', '').strip(),
                'ssd': self.request.POST.get('ssd_qty', '').strip(),
            }

            # STEP 1: Return all existing components (processor, ram, hdd, ssd) to 'Solv-IT'
            

            # STEP 2: Assign selected components to this serial number
            for component in components:
                print('component 891', component)
                item_raw = self.request.POST.get(component, '').strip()
                qty_raw = self.request.POST.get(f"{component}_qty", '').strip()
                qty = int(qty_raw) if qty_raw.isdigit() else 0

                
                item_list = [i.strip() for i in item_raw.split(",") if i.strip()]
                qty_list = [q.strip() for q in qty_raw.split(",") if q.strip()]

                print('item_list, qty_list', item_list, qty_list)

                # if not item_raw or qty <= 0:
                #     continue

                clean_name = item_raw.split(' X(')[0].strip()
                print(f"🔄 Updating {component.upper()} for {serialno}: {clean_name} x {qty}")

                # ✅ Return only the current component to Solv-IT
                existing_items = catogaryitem.objects.filter(serial_no=serialno, category=component)
                for item in existing_items:
                    print(f"♻️ Returning {item.category.upper()}: {item.name} X {item.quantity}")

                    central_item, created = catogaryitem.objects.get_or_create(
                        name=item.name.upper(),
                        category=component,
                        serial_no='Solv-IT',
                        updated_by = self.request.user,
                        defaults={
                            'quantity': 0,
                            'unit_price': item.unit_price,
                        }
                    )
                    central_item.quantity += item.quantity
                    central_item.updated_by = self.request.user
                    central_item.save()
                    item.delete()

                for name, qty_str in zip(item_list, qty_list):
                    try:
                        qty = int(qty_str)
                    except ValueError:
                        messages.error(self.request, f"Invalid quantity '{qty_str}' for {name}")
                        return redirect('productslist')

                    if qty <= 0:
                        continue

                    
                    print(f"✅ Processing {component.upper()}: {name} | Qty: {qty}")

                    # Fetch from 'Solv-IT' stock
                    try:
                        available_item = catogaryitem.objects.get(
                            name=name,
                            category=component,
                            serial_no='Solv-IT'
                        )
                    except catogaryitem.DoesNotExist:
                        assigned_item1, created = catogaryitem.objects.get_or_create(
                            name=name.upper(),
                            category=component,
                            serial_no=serialno,
                            updated_by = self.request.user,
                            defaults={
                                'quantity': qty,
                                'unit_price': 0,  # or some fallback
                            }
                        )
                        if not created:
                            assigned_item1.quantity += qty
                            assigned_item1.updated_by = self.request.user
                            assigned_item1.save()
                        print(f"⚠️ '{name}' not found in Solv-IT, but added directly to {serialno}.")
                        messages.success(self.request,f"⚠️ '{name}' not found in Solv-IT, but added directly to {serialno}.")
                        continue

                    if available_item.quantity < qty:
                        print(f"Not enough '{name}' available in {component}")
                        messages.error(self.request, f"Not enough '{name}' available in {component}.")
                        return redirect('productslist')

                    # Deduct from stock
                    available_item.quantity -= qty
                    if available_item.quantity <= 0:
                        available_item.delete()
                    else:
                        available_item.save()

                    # Assign to target serial number
                    assigned_item, created = catogaryitem.objects.get_or_create(
                        name=name,
                        category=component,
                        serial_no=serialno,
                        updated_by = self.request.user,
                        defaults={
                            'quantity': 0,
                            'unit_price': available_item.unit_price,
                        }
                    )
                    assigned_item.quantity += qty
                    assigned_item.updated_by = self.request.user
                    assigned_item.save()

                    messages.success(
                        self.request,
                        f"✅ Assigned {qty} of '{name}' to {serialno}. {'Created new' if created else 'Updated existing'}."
                    )
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
    context_object_name = 'catogaryitem'
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
    
    def form_valid(self, form):
        # Set created_by and timestamps on the instance and let the
        # superclass save the object (avoids double-saving).
        form.instance.created_by = getattr(self.request, 'user', None)
        now = timezone.now()
        form.instance.created_date = now
        form.instance.updated_date = now
        form.instance.updated_by = getattr(self.request, 'user', None)
        return super().form_valid(form)


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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            term = request.POST.get("term", "").strip()
            print("📥 Received POST Data:", request.POST)
            print("🔍 Search Term:", term)

            if not term:
                return JsonResponse({'error': 'No search term provided'}, status=400)

            # Match Items
            items = Item.objects.filter(serialno__icontains=term)
            if not items.exists():
                print('🔄 Searching in purchased items')
                items = Itempurchased.objects.filter(serialno__icontains=term)
            print("✅ Matching Items Found:", items.count())

            data = []
            for item in items[:10]:
                # Get category details for each item's serial number
                category_items = catogaryitem.objects.filter(serial_no=item.serialno)
                if not category_items.exists():
                    print('🔄 Searching in purchased category items')
                    category_items = catogaryitempurchased.objects.filter(serial_no=item.serialno)
                print(f"📦 Category items for {item.serialno}: {category_items.count()}")

                # Build description
                # description_parts = []
                # for cat_item in category_items:
                #     description_parts.append(f"{cat_item.category.capitalize()}: {cat_item.name}")
                #     print(f"🔧 {cat_item.category}: {cat_item.name}")

                description_parts = []
                for cat_item in category_items:
                    print('cat_itemcat_item',cat_item.category, cat_item.name)
                    description_parts.append(f"<span class='badge bg-secondary me-1'>{cat_item.category.capitalize()}: {cat_item.name}</span>")
                description = " ".join(description_parts)


                description = ", ".join(description_parts)

                # Build response object
                print('description', description)
                item_data = {
                    'id': item.id,
                    'name': item.name,
                    'serial_no': item.serialno,
                    'description': description,
                    'price': item.price,
                    'quantity': item.quantity,
                    # 'total_item': float(item.unit_price) * item.quantity
                }

                print("📄 Final Item Data:", item_data)
                data.append(item_data)

            return JsonResponse(data, safe=False)

        except Exception as e:
            print("❌ Error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    print("⚠️ Not an AJAX request")
    return JsonResponse({'error': 'Not an AJAX request'}, status=400)






from django.http import JsonResponse
from .models import Item  # Replace with your model

@login_required
@csrf_exempt
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


@login_required
@csrf_exempt
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


@login_required
@csrf_exempt
def add_processor1(request):
    serialno = request.GET.get('serialno', '')
    if serialno:
        processors = Processor.objects.filter(serial_no=serialno)
        processor_list = [{"id": processor.id, "name": processor.name} for processor in processors]
        return JsonResponse({"processors": processor_list, 'success': True})
    return JsonResponse({"processors": [], 'success': False})

# View for adding a new Processor

@login_required
@csrf_exempt
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

@login_required
@csrf_exempt
def add_hdd(request):
    if request.method == 'POST' and request.is_ajax():
        form = HddForm(request.POST)
        if form.is_valid():
            hdd = form.save()
            return JsonResponse({'success': True, 'id': hdd.id, 'name': hdd.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        
# View for adding a new HDD

@login_required
@csrf_exempt
def add_ram(request):
    if request.method == 'POST' and request.is_ajax():
        form = RamForm(request.POST)
        if form.is_valid():
            ram = form.save()
            return JsonResponse({'success': True, 'id': ram.id, 'name': ram.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

# View for adding a new SSD

@login_required
@csrf_exempt
def add_ssd(request):
    if request.method == 'POST' and request.is_ajax():
        form = SddForm(request.POST)
        if form.is_valid():
            ssd = form.save()
            return JsonResponse({'success': True, 'id': ssd.id, 'name': ssd.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        

@login_required
@csrf_exempt
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
        

@login_required
@csrf_exempt
def get_category_items(request):
    serial = request.GET.get("serial", "")
    name = request.GET.get("name", "")
    if serial:
        data = {
            "processors": list(catogaryitem.objects.filter(category='processor', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
            "rams": list(catogaryitem.objects.filter(category='ram', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
            "hdds": list(catogaryitem.objects.filter(category='hdd', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
            "ssds": list(catogaryitem.objects.filter(category='ssd', serial_no__icontains=serial).values("id", "name", "quantity", "serial_no")),
        }
    elif name:
        data = {
            "processors": list(catogaryitem.objects.filter(category='processor', name__icontains=name,  serial_no__icontains='Solv-IT', quantity__gte=1).values("id", "name", "quantity", "serial_no")),
            "rams": list(catogaryitem.objects.filter(category='ram', name__icontains=name,  serial_no__icontains='Solv-IT', quantity__gte=1).values("id", "name", "quantity", "serial_no")),
            "hdds": list(catogaryitem.objects.filter(category='hdd', name__icontains=name,  serial_no__icontains='Solv-IT', quantity__gte=1).values("id", "name", "quantity", "serial_no")),
            "ssds": list(catogaryitem.objects.filter(category='ssd', name__icontains=name,  serial_no__icontains='Solv-IT', quantity__gte=1).values("id", "name", "quantity", "serial_no")),
        }
    else:
        # Default to empty lists for all categories if neither serial nor name is provided
        data = {
            "processors": [],
            "rams": [],
            "hdds": [],
            "ssds": []
        }

    print('data', data)
    
    return JsonResponse(data)

@login_required
@csrf_exempt
def operativedashboard(request):
    user_profile = request.user.profile
    if user_profile.role == 'OP':
        return render(request, "store/operative_productupdate.html")
    else:
        return render(request, "store/productslist.html")


@csrf_exempt
def create_category_items(spec_string, serial_no, category, quantity,price,createdby,product_code):
    print(f"create_category_items called with serial_no={serial_no}, category={category}, spec_string={spec_string}, quantity={quantity}, createdby={createdby}, product_code={product_code}")
    spec_string = '' if spec_string is None else spec_string
    quantity = '' if quantity is None else quantity
    price = '' if price is None else price
    
    names = [n.strip() for n in str(spec_string).split(',') if n.strip()]
    quantitys = [n for n in str(quantity).split(',') if n]
    for name, quantity in zip( names, quantitys) :
        catogaryitem.objects.create(
            name=name.upper(),
            serial_no=serial_no,
            category=category,
            quantity=quantity,
            unit_price=price,
            created_by=createdby,
            purchase_lot_code = product_code
        )


@csrf_exempt
def create_category_itemsproduct(spec_string, serial_no, category, quantity, price, createdby, purchased_code):
    """
    Robust creation helper for catogaryitem rows from CSV/Excel cell values.

    - spec_string: comma separated names (can be empty / NaN)
    - quantity: comma separated quantities (numbers or strings)
    - price: unit price (may be empty)
    """
    try:
        print(f"create_category_items called with serial_no={serial_no}, category={category}, spec_string={spec_string}, quantity={quantity}, price={price}, createdby={createdby}, purchased_code={purchased_code}")
        # Normalize inputs and guard against pandas NaN
        spec_string = '' if spec_string is None else spec_string
        quantity = '' if quantity is None else quantity
        price = '' if price is None else price

        names = [n.strip() for n in str(spec_string).split(',') if n and str(n).strip().lower() not in ('nan', '')]
        quantitys = [q.strip() for q in str(quantity).split(',') if q and str(q).strip().lower() not in ('nan', '')]

        # If only one quantity provided but many names, repeat that quantity
        pairs = list(zip_longest(names, quantitys, fillvalue='1'))

        for name, qty in pairs:
            if not name:
                continue
            # parse quantity to int (fallback to 1)
            try:
                qty_val = int(float(str(qty)))
            except Exception:
                qty_val = 1

            # parse price to float (fallback to 0.0)
            try:
                price_val = float(str(price)) if str(price).strip().lower() not in ('', 'nan') else 0.0
            except Exception:
                price_val = 0.0

            catogaryitem.objects.create(
                name=str(name).upper(),
                serial_no=str(serial_no),
                category=str(category),
                quantity=qty_val,
                unit_price=price_val,
                purchase_lot_code=str(purchased_code) if purchased_code is not None else '',
                created_by=createdby
            )
    except Exception as e:
        # Log and re-raise so the caller can decide how to handle it (or swallow if desired)
        print(f"create_category_items error for serial {serial_no} category {category}: {e}")
        raise

@csrf_exempt
def create_category_itemspurchase(spec_string, serial_no, category, quantity, createdby, purchased_code):
    try:
        spec_string = '' if spec_string is None else spec_string
        quantity = '' if quantity is None else quantity
        names = [n.strip() for n in str(spec_string).split(',') if n and str(n).strip().lower() not in ('nan', '')]
        quantitys = [q.strip() for q in str(quantity).split(',') if q and str(q).strip().lower() not in ('nan', '')]

        pairs = list(zip_longest(names, quantitys, fillvalue='1'))
        for name, qty in pairs:
            if not name:
                continue
            try:
                qty_val = int(float(str(qty)))
            except Exception:
                qty_val = 1

            catogaryitempurchased.objects.create(
                name=str(name).upper(),
                serial_no=str(serial_no),
                category=str(category),
                quantity=qty_val,
                unit_price=0.0,
                purchase_lot_code=str(purchased_code) if purchased_code is not None else '',
                created_by=createdby
            )
    except Exception as e:
        print(f"create_category_itemspurchase error for serial {serial_no} category {category}: {e}")
        raise


@csrf_exempt
def upload_category_items(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            # try:
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                print(row)
                serial_no = str(row.get('Serialno')).strip()
                name = row.get('Name', '').strip()
                vendor_name = str(row.get('vendor_name', '')).strip()
                customer_name = str(row.get('customer_name', '')).strip()
                purchased_code = str(row.get('purchased_code', '')).strip()

                print('dadadadad', vendor_name, purchased_code)

                vendor = Vendor.objects.filter(name__iexact=vendor_name).first()
                customer = Customer.objects.filter(first_name__iexact=customer_name).first()
                if not vendor and vendor_name:
                    vendor = Vendor.objects.create(name=vendor_name)
                if vendor:
                    Itempurchased.objects.create(
                    name=name,
                    serialno=serial_no,
                    make_and_models=row.get('Make and models', ''),
                    smps_status=row.get('Smps / Adapter status', '').strip(),
                    motherboard_status=row.get('Motherboard status', '').strip(),
                    quantity=row.get('Quantity', 1),
                    price=row.get('Price', 0.0),
                    note=row.get('Note', '').strip(),
                    vendor_name=vendor,
                    purchased_code=purchased_code,
                    customer=customer_name,
                    created_by = request.user
                    )

                    # print('12345', row.get('Processor', ''), serial_no, 'processor', row.get('processor_qty', ''), request.user)
                    # Inside your row loop
                    create_category_itemspurchase(row.get('Processor', ''), serial_no, 'processor', row.get('Processor_Qty', ''), request.user, purchased_code)
                    create_category_items(row.get('RAM', ''), serial_no, 'ram', row.get('Ram_Qty', ''), request.user, purchased_code)
                    create_category_itemspurchase(row.get('Hdd ', ''), serial_no, 'hdd', row.get('Hdd_Qty', ''), request.user, purchased_code)
                    create_category_itemspurchase(row.get('Sdd', ''), serial_no, 'ssd',row.get('Ssd_Qty', ''), request.user, purchased_code)
                    return render(request, 'transactions/purchasecreate.html', {
                        'form': ExcelUploadForm(),
                        'success': "Excel imported successfully!"
                    })
                else:
                    # Create the Item entry
                    item = Item.objects.create(
                        name=name,
                        serialno=serial_no,
                        make_and_models=row.get('Make and models', ''),
                        smps_status=row.get('Smps / Adapter status', '').strip(),
                        motherboard_status=row.get('Motherboard status', '').strip(),
                        quantity=row.get('Quantity', 1),
                        price=row.get('Price', 0.0),
                        note=row.get('Note', '').strip(),
                        purchased_code=purchased_code,
                        customer=customer,
                        created_by=request.user
                    )

                    # print('12345', row.get('Processor', ''), serial_no, 'processor', row.get('processor_qty', ''), request.user)
                    # Inside your row loop
                    create_category_items(row.get('Processor', ''), serial_no, 'processor', row.get('Processor_Qty', ''),0.0, request.user, purchased_code)
                    create_category_items(row.get('RAM', ''), serial_no, 'ram', row.get('Ram_Qty', ''),0.0, request.user, purchased_code)
                    create_category_items(row.get('HDD', ''), serial_no, 'hdd', row.get('Hdd_Qty', ''),0.0, request.user, purchased_code)
                    create_category_items(row.get('SSD', ''), serial_no, 'ssd',row.get('Ssd_Qty', ''),0.0, request.user, purchased_code)


                    return render(request, 'store/productcreate.html', {
                        'form': ExcelUploadForm(),
                        'success': "Excel imported successfully!"
                    })

            # except Exception as e:
            #     return render(request, 'store/productcreate.html', {
            #         'form': form,
            #         'error': f"Import failed: {e}"
            #     })
    else:
        form = ExcelUploadForm()

    return render(request, 'store/productcreate.html', {'form': form})



@csrf_exempt
def upload_category_only(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            # try:
            # Read and replace NaN with empty strings to avoid 'nan' and float issues
            df = pd.read_excel(excel_file).fillna('')

            print('df', df.head())

            # Build normalized map of columns once to support flexible header names
            norm_map = {}
            for c in df.columns:
                if c is None:
                    continue
                norm_map[str(c).strip().lower()] = c

            print(f"upload_category_only: normalized columns detected: {list(norm_map.keys())}")

            def find_col(possible_substrings):
                for k, orig in norm_map.items():
                    for sub in possible_substrings:
                        if sub in k:
                            return orig
                return None

            serial_col = find_col(['serial', 'serialno', 'serial number'])
            name_col = find_col(['name', 'item', 'product'])
            category_col = find_col(['Category', 'cat', 'component', 'type'])
            qty_col = find_col(['quantity', 'qty'])
            price_col = find_col(['unit price', 'unit_price', 'price', 'unitprice'])
            vendor_col = find_col(['vendor', 'product code', 'vendor name', 'product code / vendor name'])
            purchased_col = find_col(['purchased_code', 'purchased code', 'purchase code', 'product code', 'product code / vendor name'])

            for row_idx, row in df.iterrows():
                serial_no = str(row.get(serial_col, '')).strip() if serial_col else ''
                row_category = str(row.get(category_col, '')).strip() if category_col else ''
                comp_name = str(row.get(d, '')).strip() if name_col else ''
                qty_val = row.get(qty_col, '') if qty_col else 1
                unit_price = 0.0 #row.get(price_col, '') if price_col else ''
                vendor_name = str(row.get(vendor_col, '')).strip() if vendor_col else ''
                purchased_code = str(row.get(purchased_col, '')).strip() if purchased_col else ''

                print(f"upload_category_only: row {row_idx} -> serial_no={serial_no}, category={row_category}, name={comp_name}, qty={qty_val}, price={unit_price}, purchased_code={purchased_code}")

                # If row has category+name populate a single catogaryitem
                try:
                    if row_category and comp_name:
                        print(f"upload_category_only: creating single category item for serial {serial_no}, category {row_category}, name {comp_name}, qty {qty_val}, price {unit_price}")
                        create_category_items(comp_name, serial_no, row_category.strip(), str(qty_val), unit_price, request.user, purchased_code)
                    else:
                        print(f"upload_category_only: no single category+name found for row {row_idx}, falling back to wide-columns")
                        # Fallback: wide-columns Processor/Ram/Hdd/Ssd
                        proc_spec = str(row.get('Processor', '') or '').strip()
                        ram_spec = str(row.get('Ram', '') or '').strip()
                        hdd_spec = str(row.get('Hdd', '') or '').strip()
                        ssd_spec = str(row.get('Ssd', '') or '').strip()

                    create_category_items(row.get('Processors', ''), serial_no, 'processor', row.get('Processor_Qty', ''),0.0, request.user, purchased_code)
                    create_category_items(row.get('RAMs', ''), serial_no, 'ram', row.get('Ram_Qty', ''),0.0, request.user, purchased_code)
                    create_category_items(row.get('HDDs', ''), serial_no, 'hdd', row.get('Hdd_Qty', ''),0.0, request.user, purchased_code)
                    create_category_items(row.get('SSDs', ''), serial_no, 'ssd',row.get('Ssd_Qty', ''),0.0, request.user, purchased_code)
                except Exception as e:
                    print(f"upload_category_only: failed to create category items for serial {serial_no} at row {row_idx}: {e}")
                    return render(request, 'store/category_form.html', {
                        'form': ExcelUploadForm(),
                        'error': f"Import failed for serial {serial_no} at row {row_idx}: {e}"
                    })

            return render(request, 'store/category_form.html', {
                'form': ExcelUploadForm(),
                'success': "Excel imported successfully!"
            })

            # except Exception as e:
            #     return render(request, 'store/productcreate.html', {
            #         'form': form,
            #         'error': f"Import failed: {e}"
            #     })
    else:
        form = ExcelUploadForm()

    return render(request, 'store/category_form.html', {'form': form})












        



