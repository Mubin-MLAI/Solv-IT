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

# Django core imports
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
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

# Local app imports
from accounts.models import Profile, Vendor
from transactions.models import Sale
from .models import  Item, Delivery, Ram, Sdd, Hdd, Processor , catogaryitem  #, Nvme, M_2
from .forms import ItemForm,  DeliveryForm, RamForm, SddForm, HddForm, ProcessorForm    #, NvmeForm, M_2Form
from .tables import ItemTable, CategoryItemTable
import pandas as pd




@login_required
def dashboard(request):
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
    }
    return render(request, "store/dashboard.html", context)


class ProductListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.

    Attributes:
    - model: The model associated with the view.
    - table_class: The table class used for rendering.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    - paginate_by: Number of items per page for pagination.
    """

    model = Item
    table_class = ItemTable
    template_name = "store/productslist.html"
    context_object_name = "items"
    paginate_by = 10
    SingleTableView.table_pagination = False

class ProductListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.

    Attributes:
    - model: The model associated with the view.
    - table_class: The table class used for rendering.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    - paginate_by: Number of items per page for pagination.
    """

    model = Item
    table_class = ItemTable
    template_name = "store/productslist.html"
    context_object_name = "items"
    paginate_by = 10
    SingleTableView.table_pagination = False


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
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_, (Q(name__icontains=q) | Q(serialno__icontains=q) | Q(make_and_models__icontains=q) for q in query_list)
                )
            )
        return result


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


# class ProductCreateView(LoginRequiredMixin, CreateView):
#     """
#     View class to create a new product.

#     Attributes:
#     - model: The model associated with the view.
#     - template_name: The HTML template used for rendering the view.
#     - form_class: The form class used for data input.
#     - success_url: The URL to redirect to upon successful form submission.
#     """

#     model = Item
#     template_name = "store/productcreate.html"
#     form_class = ItemForm
#     success_url = "/products"

#     def test_func(self):
#         # item = Item.objects.get(id=pk)
#         if self.request.POST.get("quantity") < 1:
#             return False
#         else:
#             return True

# from django.urls import reverse_lazy
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic.edit import CreateView
# from .forms import ItemForm
# from .models import Item

# class ProductCreateView(LoginRequiredMixin, CreateView):
#     """
#     View class to create a new product.

#     Attributes:
#     - model: The model associated with the view.
#     - template_name: The HTML template used for rendering the view.
#     - form_class: The form class used for data input.
#     - success_url: The URL to redirect to upon successful form submission.
#     """

#     model = Item
#     template_name = "store/productcreate.html"
#     form_class = ItemForm
#     success_url = reverse_lazy('products')  # Use reverse_lazy to ensure correct URL resolution

#     def form_valid(self, form):
#         # Get the quantity from the form's cleaned data
#         quantity = form.cleaned_data.get('ram_qty')
#         print('qty', quantity)

#         # Check if quantity is valid
#         if quantity < 1:
#             form.add_error('quantity', 'Quantity must be at least 1.')  # Add error if quantity is invalid
#             form.save()
#             return self.form_invalid(form)

#         # Save the product instance
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         # Handle invalid form submission
#         return super().form_invalid(form)

#     def test_func(self):
#         """
#         Check if the user has permission to create a product.
#         Here you can add any user-specific permission logic.
#         """
#         # Example permission check: Only allow users with staff status to create products
#         return self.request.user.is_staff


from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import ItemForm
from .models import Item

# class ProductCreateView(CreateView):
"""
View class to create a new product.

Attributes:
- model: The model associated with the view.
- template_name: The HTML template used for rendering the view.
- form_class: The form class used for data input.
- success_url: The URL to redirect to upon successful form submission.
"""
# def productcreateview(request):
#     if request.method == 'POST':
#         form = ItemForm(request.POST)
#         if form.is_valid():
#             # Save the product to the database
#             form.save()
#             return redirect('productslist')  # Redirect to the product list or success page
#     else:
#         form = ItemForm()
#     return render(request, 'store/productcreate.html', {'form': form})

def productcreateview(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()

            quantity=item.processor_qty + item.ram_qty + item.hdd_qty + item.ssd_qty

            # for i in range(0,quantity):
            if item.processor_qty <= 1:
                # Now create the corresponding Product record
                product = catogaryitem(
                    category='Processor',  # Use the category from Item
                    name=item.processor,  # Use the same name from Item
                    serial_no=item.serialno,  # Same serial number from Item
                    quantity=item.processor_qty,  # This could vary depending on your quantity logic
                    unit_price=0.00  # Assuming a fixed price for the product, this can be dynamic too
                    )
                product.save()  # Save the product to the Product table
                
            if item.ram_qty <= 1:
                # Now create the corresponding Product record
                product = catogaryitem(
                    category='RAM',  # Use the category from Item
                    name=item.ram,  # Use the same name from Item
                    serial_no=item.serialno,  # Same serial number from Item
                    quantity=item.ram_qty,  # This could vary depending on your quantity logic
                    unit_price=0.00  # Assuming a fixed price for the product, this can be dynamic too
                    )
            
                product.save()  # Save the product to the Product table
            
            if item.hdd_qty <= 1:
                # Now create the corresponding Product record
                product = catogaryitem(
                    category='HDD',  # Use the category from Item
                    name=item.hdd,  # Use the same name from Item
                    serial_no=item.serialno,  # Same serial number from Item
                    quantity=item.hdd_qty,  # This could vary depending on your quantity logic
                    unit_price=0.00  # Assuming a fixed price for the product, this can be dynamic too
                    )
            
                product.save()  # Save the product to the Product table
            
            if item.ssd_qty <= 1:
                # Now create the corresponding Product record
                product = catogaryitem(
                    category='SSD',  # Use the category from Item
                    name=item.ssd,  # Use the same name from Item
                    serial_no=item.serialno,  # Same serial number from Item
                    quantity=item.ssd_qty,  # This could vary depending on your quantity logic
                    unit_price=0.00  # Assuming a fixed price for the product, this can be dynamic too
                    )
            
                product.save()  # Save the product to the Product table
                

            return redirect('productslist')  # Redirect to a list page or wherever needed
    else:
        form = ItemForm()
    return render(request, 'store/productcreate.html', {'form': form})




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
    template_name = "store/productupdate.html"
    form_class = ItemForm
    success_url = "/products"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


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
    form_class = RamForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})

class HddCategoryCreateView(LoginRequiredMixin, CreateView):
    model = Hdd
    template_name = 'store/Hdd_form.html'
    form_class = HddForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = catogaryitem
    template_name = 'store/category_form.html'
    form_class = RamForm
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
    if is_ajax(request):
        try:
            term = request.POST.get("term", "")
            data = []

            items = Item.objects.filter(name__icontains=term)
            for item in items[:10]:
                data.append(item.to_json())

            return JsonResponse(data, safe=False)
        except Exception as e:
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

