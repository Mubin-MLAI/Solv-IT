# Standard library imports
import json
import logging

# Django core imports
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.db import transaction
from django.core.paginator import Paginator

# Class-based views
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Authentication and permissions
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Third-party packages
from openpyxl import Workbook
from openpyxl.styles import Alignment

# Local app imports
from store.models import Item
from accounts.models import Customer
from .models import Sale, Purchase, SaleDetail, Bankaccount
from .forms import PurchaseForm, BankForm
from store.models import catogaryitem 


logger = logging.getLogger(__name__)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def export_bank_to_excel(request):
    # Create a workbook and select the active worksheet.
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Bank Details'

    # Define the column headers
    columns = [
        'ID', 'Account Name', 'Opening Balance', 'As Of Date'
    ]
    worksheet.append(columns)

    # Fetch sales data
    banks = Bankaccount.objects.all()

    for bank in banks:
        # Convert timezone-aware datetime to naive datetime
        if bank.as_of_date.tzinfo is not None:
            as_of_date = bank.as_of_date.replace(tzinfo=None)
        else:
            as_of_date = bank.as_of_date

        worksheet.append([
            bank.id,
            bank.account_name,
            bank.opening_balance,
            as_of_date
        ])

    # Set up the response to send the file
    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    )
    response['Content-Disposition'] = 'attachment; filename=Bank Details.xlsx'
    workbook.save(response)

    return response


from openpyxl import Workbook
from django.http import HttpResponse
from .models import Sale  # Adjust if needed
import datetime

def export_sales_to_excel(request):
    # Create a workbook and sheet
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Sales'

    # Define headers (added 'Item Descriptions')
    columns = [
        'INV no', 'Date', 'Customer', 'Sub Total',
        'Grand Total', 'Tax Amount', 'Tax Percentage',
        'Amount Paid', 'Amount Change', 'Item Descriptions'
    ]
    worksheet.append(columns)

    # Fetch all sales
    sales = Sale.objects.all()

    for sale in sales:
        # Handle datetime conversion
        date_added = sale.date_added.replace(tzinfo=None) if sale.date_added.tzinfo else sale.date_added

        # Generate item descriptions
        items = sale.get_item_descriptions_by_type()
        description_lines = []

        for category in ['PROCESSOR', 'RAM', 'HDD', 'SSD']:
            category_items = items.get(category, [])
            for line in category_items:
                description_lines.append(line.strip())

        description_text = "\n".join(description_lines)  # Line-by-line text

        # Add row data
        row_data = [
            'INV'+ str(sale.id),
            date_added,
            sale.customer.phone,
            sale.sub_total,
            sale.grand_total,
            sale.tax_amount,
            sale.tax_percentage,
            sale.amount_paid,
            sale.amount_change,
            description_text
        ]

        worksheet.append(row_data)

        # Apply wrap text to the "Item Descriptions" column
        description_cell = worksheet.cell(row=worksheet.max_row, column=10)
        description_cell.alignment = Alignment(wrap_text=True)

    # Adjust column widths (optional)
    for col in worksheet.columns:
        max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
        worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=sales.xlsx'
    workbook.save(response)
    return response



def export_purchases_to_excel(request):
    # Create a workbook and select the active worksheet.
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Purchases'

    # Define the column headers
    columns = [
        'ID', 'Item', 'Description', 'Vendor', 'Order Date',
        'Delivery Date', 'Quantity', 'Delivery Status',
        'Price per item (Ksh)', 'Total Value'
    ]
    worksheet.append(columns)

    # Fetch purchases data
    purchases = Purchase.objects.all()

    for purchase in purchases:
        # Convert timezone-aware datetime to naive datetime
        delivery_tzinfo = purchase.delivery_date.tzinfo
        order_tzinfo = purchase.order_date.tzinfo

        if delivery_tzinfo or order_tzinfo is not None:
            delivery_date = purchase.delivery_date.replace(tzinfo=None)
            order_date = purchase.order_date.replace(tzinfo=None)
        else:
            delivery_date = purchase.delivery_date
            order_date = purchase.order_date
        worksheet.append([
            purchase.id,
            purchase.item.name,
            purchase.description,
            purchase.vendor.name,
            order_date,
            delivery_date,
            purchase.quantity,
            purchase.get_delivery_status_display(),
            purchase.price,
            purchase.total_value
        ])

    # Set up the response to send the file
    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    )
    response['Content-Disposition'] = 'attachment; filename=purchases.xlsx'
    workbook.save(response)

    return response

from django.db.models import Q

class SaleListView(ListView):
    model = Sale
    template_name = 'transactions/sales_list.html'
    context_object_name = 'sales'
    paginate_by = 10

    def get_queryset(self):
        sales = Sale.objects.all().prefetch_related('saledetail_set__item')
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        serial_filter = self.request.GET.get('serial')
        inv = self.request.GET.get('inv')

        if status:
            queryset = queryset.filter(status=status)

        if inv:
            # Assuming invoice number is derived from `id`, e.g., INV123
            if inv.lower().startswith("inv"):
                inv = inv[3:]  # Strip "INV" prefix
            if inv.isdigit():
                queryset = queryset.filter(id=inv)
            else:
                queryset = queryset.none()

        if serial_filter:
            queryset = sales.filter(saledetail_set__item__serialno__icontains=serial_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class SaleDetailView(LoginRequiredMixin, DetailView):
    """
    View to display details of a specific sale.
    """
    model = Sale
    template_name = "transactions/invoice.html"
    context_object_name = "sale"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale = self.get_object()
        context["total_after_payment"] = sale.grand_total - sale.amount_paid
        return context




from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
import json
import logging
from .models import Customer, Item, Sale, SaleDetail

logger = logging.getLogger(__name__)

def SaleCreateView(request):
    context = {
        "active_icon": "sales",
        "customers": [c.to_select2() for c in Customer.objects.all()],
        "items": [d.to_select3() for d in Item.objects.all()],
        "bank_accounts": Bankaccount.objects.all()
    }

    if request.method == 'POST' and is_ajax(request=request):
        try:
            data = json.loads(request.body)
            logger.info(f"Received data: {data}")

            # ✅ Add 'payment_type' to required fields
            required_fields = [
                'customer', 'sub_total', 'grand_total',
                'amount_paid', 'amount_change', 'items', 'payment_type'
            ]

            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # ✅ Validate bank account only if payment type is 'Bank'
            bank_account = None
            if data['payment_type'] == 'Bank':
                if 'bank_account' not in data or not data['bank_account']:
                    raise ValueError("Bank account must be provided for Bank payments")
                try:
                    bank_account = Bankaccount.objects.get(id=int(data['bank_account']))
                except Bankaccount.DoesNotExist:
                    raise ValueError("Invalid bank account selected")
                
            # Calculate dynamic status
            amount_paid = float(data["amount_paid"])
            grand_total = float(data["grand_total"])

            if amount_paid >= grand_total:
                sale_status = 'Paid'
            elif amount_paid == 0:
                sale_status = 'Unpaid'
            else:
                sale_status = 'Balance'

            # ✅ Build sale (main) attributes
            sale_attributes = {
                "customer": Customer.objects.get(id=int(data['customer'])),
                "sub_total": float(data["sub_total"]),
                "grand_total": float(data["grand_total"]),
                "tax_amount": float(data.get("tax_amount", 0.0)),
                "tax_percentage": float(data.get("tax_percentage", 0.0)),
                "amount_paid": float(data["amount_paid"]),
                "amount_change": float(data["amount_change"]),
                "payment_type": data['payment_type'],
                "bank_account": bank_account,
                "status": sale_status  # <-- Now saving dynamic status
            }
            with transaction.atomic():
                # ✅ Create Sale (master)
                new_sale = Sale.objects.create(**sale_attributes)
                logger.info(f"Sale created: {new_sale}")

                # ✅ Process each item
                items = data["items"]
                if not isinstance(items, list):
                    raise ValueError("Items should be a list")

                for item in items:
                    if not all(k in item for k in ["id", "price", "quantity", "total_item"]):
                        raise ValueError("Item is missing required fields")

                    item_instance = Item.objects.get(id=int(item["id"]))

                    if item_instance.quantity < int(item["quantity"]):
                        raise ValueError(f"Not enough stock for item: {item_instance.name}")

                    # ✅ Auto-generate description
                    components = catogaryitem.objects.filter(serial_no=item_instance.serialno)
                    grouped = {
                        'processor': [],
                        'ram': [],
                        'hdd': [],
                        'ssd': []
                    }

                    for comp in components:
                        grouped[comp.category].append(f"{comp.name} X({comp.quantity})")

                    description = ""
                    for cat in ['processor', 'ram', 'hdd', 'ssd']:
                        if grouped[cat]:
                            category_display = cat.upper()
                            values = ", ".join(grouped[cat])
                            description += f"{category_display}: {values} ({comp.serial_no})<br>"

                    # ✅ Create SaleDetail with generated description
                    SaleDetail.objects.create(
                        sale=new_sale,
                        item=item_instance,
                        quantity=int(item["quantity"]),
                        price=float(item["price"]),
                        total_detail=float(item["total_item"]),
                        description=description  # Auto-generated HTML
                    )

                    # ✅ Update stock
                    item_instance.quantity -= int(item["quantity"])
                    item_instance.save()

                
                

            return JsonResponse({
                'status': 'success',
                'message': 'Sale created successfully!',
                'redirect': '/transactions/sales/'
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body!'}, status=400)
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer does not exist!'}, status=400)
        except Item.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item does not exist!'}, status=400)
        except ValueError as ve:
            return JsonResponse({'status': 'error', 'message': f'Value error: {str(ve)}'}, status=400)
        except TypeError as te:
            return JsonResponse({'status': 'error', 'message': f'Type error: {str(te)}'}, status=400)
        except Exception as e:
            logger.error(f"Exception during sale creation: {e}")
            return JsonResponse({'status': 'error', 'message': f'There was an error during the creation: {str(e)}'}, status=500)

    return render(request, "transactions/sale_create.html", context=context)


# def SaleCreateView(request):
#     context = {
#         "active_icon": "sales",
#         "customers": [c.to_select2() for c in Customer.objects.all()],
#         "items": [d.to_select3() for d in Item.objects.all()]
#     }

#     if request.method == 'POST':
#         if is_ajax(request=request):
#             try:
#                 # Load the JSON data from the request body
#                 data = json.loads(request.body)
#                 print('logger', f"Received data: {data}")
#                 logger.info(f"Received data: {data}")

#                 # Validate required fields
#                 required_fields = [
#                     'customer','item','sub_total', 'grand_total',
#                     'amount_paid', 'amount_change', 'items'
#                 ]
#                 for field in required_fields:
#                     if field not in data:
#                         raise ValueError(f"Missing required field: {field}")

#                 print('tax_amount tax_percentage',float(data.get("tax_amount", 0.0)), float(data.get("tax_percentage", 0.0)))
#                 # Create sale attributes
#                 sale_attributes = {
#                     "customer": Customer.objects.get(id=int(data['customer'])),
#                     "item": Item.objects.get(id=int(data['items'][0]['id'])),
#                     "sub_total": float(data["sub_total"]),
#                     "grand_total": float(data["grand_total"]),
#                     "tax_amount": float(data.get("tax_amount", 0.0)),
#                     "tax_percentage": float(data.get("tax_percentage", 0.0)),
#                     "amount_paid": float(data["amount_paid"]),
#                     "amount_change": float(data["amount_change"]),
#                 }

#                 # Use a transaction to ensure atomicity
#                 with transaction.atomic():
#                     # Create the sale
#                     new_sale = Sale.objects.create(**sale_attributes)
#                     print('Sale created: {new_sale}')
#                     logger.info(f"Sale created: {new_sale}")

#                     # Create sale details and update item quantities
#                     items = data["items"]
#                     if not isinstance(items, list):
#                         raise ValueError("Items should be a list")

#                     for item in items:
#                         if not all(
#                             k in item for k in [
#                                 "id", "price", "quantity", "total_item"
#                             ]
#                         ):
#                             raise ValueError("Item is missing required fields")
                        
#                         print('int(item["id"])', int(item["id"]))
                        

#                         item_instance = Item.objects.get(id=int(item["id"]))
#                         print('item_instance.quantity,  int(item["quantity"])', item_instance.quantity , int(item["quantity"]))
#                         if item_instance.quantity < int(item["quantity"]):
#                             raise ValueError(f"Not enough stock for item: {item_instance.name}")

                        # detail_attributes = {
                        #     "sale": new_sale,
                        #     "item": item_instance,
                        #     "price": float(item["price"]),
                        #     "quantity": int(item["quantity"]),
                        #     "total_detail": float(item["total_item"])
                        # }
#                         SaleDetail.objects.create(**detail_attributes)
#                         logger.info(f"Sale detail created: {detail_attributes}")

#                         # Reduce item quantity
#                         item_instance.quantity -= int(item["quantity"])
#                         item_instance.save()

#                 return JsonResponse(
#                     {
#                         'status': 'success',
#                         'message': 'Sale created successfully!',
#                         'redirect': '/transactions/sales/'
#                     }
#                 )

#             except json.JSONDecodeError:
#                 return JsonResponse(
#                     {
#                         'status': 'error',
#                         'message': 'Invalid JSON format in request body!'
#                     }, status=400)
#             except Customer.DoesNotExist:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'Customer does not exist!'
#                     }, status=400)
#             except Item.DoesNotExist:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'Item does not exist!'
#                     }, status=400)
#             except ValueError as ve:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': f'Value error: {str(ve)}'
#                     }, status=400)
#             except TypeError as te:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': f'Type error: {str(te)}'
#                     }, status=400)
#             except Exception as e:
#                 logger.error(f"Exception during sale creation: {e}")
#                 return JsonResponse(
#                     {
#                         'status': 'error',
#                         'message': (
#                             f'There was an error during the creation: {str(e)}'
#                         )
#                     }, status=500)

#     return render(request, "transactions/sale_create.html", context=context)


class SaleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete a sale.
    """

    model = Sale
    template_name = "transactions/saledelete.html"

    def get_success_url(self):
        """
        Redirect to the sales list after successful deletion.
        """
        return reverse("saleslist")

    def test_func(self):
        """
        Allow deletion only for superusers.
        """
        return self.request.user.is_superuser


class PurchaseListView(LoginRequiredMixin, ListView):
    """
    View to list all purchases with pagination.
    """

    model = Purchase
    template_name = "transactions/purchases_list.html"
    context_object_name = "purchases"
    paginate_by = 10


class PurchaseDetailView(LoginRequiredMixin, DetailView):
    """
    View to display details of a specific purchase.
    """

    model = Purchase
    template_name = "transactions/purchasedetail.html"


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new purchase.
    """

    model = Purchase
    form_class = PurchaseForm
    template_name = "transactions/purchases_form.html"

    def get_success_url(self):
        """
        Redirect to the purchases list after successful form submission.
        """
        return reverse("purchaseslist")


class PurchaseUpdateView(LoginRequiredMixin, UpdateView):
    """
    View to update an existing purchase.
    """

    model = Purchase
    form_class = PurchaseForm
    template_name = "transactions/purchases_form.html"

    def get_success_url(self):
        """
        Redirect to the purchases list after successful form submission.
        """
        return reverse("purchaseslist")


class PurchaseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete a purchase.
    """

    model = Purchase
    template_name = "transactions/purchasedelete.html"

    def get_success_url(self):
        """
        Redirect to the purchases list after successful deletion.
        """
        return reverse("purchaseslist")

    def test_func(self):
        """
        Allow deletion only for superusers.
        """
        return self.request.user.is_superuser
    
class BankDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete a Bank.
    """

    model = Bankaccount
    template_name = "transactions/bankdelete.html"

    def get_success_url(self):
        """
        Redirect to the Bank list after successful deletion.
        """
        return reverse("cashbanklist")

    def test_func(self):
        """
        Allow deletion only for superusers.
        """
        return self.request.user.is_superuser
    
class cashbankListView(LoginRequiredMixin, ListView):
    model = Bankaccount
    template_name = "transactions/bank_acc.html"
    context_object_name = "bankaccount"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        account_id = self.request.GET.get('account_id')
        sales = Sale.objects.select_related('customer')

        if account_id:
            sales = sales.filter(bank_account_id=account_id)

        sales = sales.order_by('-date_added')
        context['sales'] = sales
        context['selected_account_id'] = account_id  # for UI highlighting if needed
        return context




class BankCreateView(LoginRequiredMixin, CreateView):
    model = Bankaccount
    template_name = "transactions/createbankacc.html"
    form_class = BankForm
        
    def get_success_url(self):
        """
        Redirect to the Bank list after successful deletion.
        """
        return reverse("cashbanklist")

    def test_func(self):
        """
        Allow deletion only for superusers.
        """
        return self.request.user.is_superuser
    

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Sale
from .forms import PaymentForm

@require_POST
def receive_payment(request):
    form = PaymentForm(request.POST)
    if form.is_valid():
        sale = get_object_or_404(Sale, id=form.cleaned_data['sale_id'])
        received = form.cleaned_data['amount_received']
        
        # Update Sale amounts
        sale.amount_paid += received
        # Calculate remaining balance
        remaining = sale.grand_total - sale.amount_paid
        
        # Update amount_change (balance due)
        sale.amount_change = max(remaining, 0)
        
        # Update status
        if remaining <= 0:
            sale.status = "Paid"
        else:
            sale.status = "Balance"  # Or "Unpaid" depending on your logic
        
        sale.save()
        
        messages.success(request, f"Payment of ₹{received:.2f} received for sale #{sale.id}.")
    else:
        messages.error(request, "Invalid payment data submitted.")
    
    return redirect('cashbanklist')  # Replace with your actual list view URL name



    

