# Django core imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local app imports
from .views import (
    PurchaseListView,
    PurchaseDetailView,
    # PurchaseCreateView,
    # PurchaseUpdateView,
    PurchaseDeleteView,
    SaleListView,
    SaleDetailView,
    SaleCreateView,
    SaleDeleteView,
    cashbankListView,
    export_sales_to_excel,
    export_purchases_to_excel,
    export_bank_to_excel,
    BankCreateView,
    BankDeleteView,
    receive_payment,
    PurchasedCreateView,
    PurchaseItemSearchListView,
    search_suggestions_purchase,
    PurchaseOrderListView,
    PurchaseCreateListView,
    receive_payment_purchase,
    # add_customer,
    customer_search,
    customer_create,
    vendor_search,
    vendor_create
)

# URL patterns
urlpatterns = [
    # Purchase URLs
    path(
        'purchase-order/',
        PurchaseOrderListView.as_view(),
        name='purchase-order-create'
    ),
    path(
        'purchase-createlist/',
        PurchaseCreateListView,
        name='purchase-create-list'
    ),
    path(
        'new-purchase/',
        PurchasedCreateView.as_view(),
        name='purchase-create'
    ),
    path('receive-payment/', receive_payment, name='receive-payment'),
    path('receive-payment-purchase/', receive_payment_purchase, name='receive-payment-purchase'),
    path('cashbankListView/', cashbankListView.as_view(), name='cashbanklist'),
    path('purchases/', PurchaseListView.as_view(), name='purchaseslist'),
    path(
         'purchase/<int:pk>/', PurchaseDetailView.as_view(),
         name='purchase-detail'
     ),
    # path(
    #      'new-purchase/', PurchaseCreateView.as_view(),
    #      name='purchase-create'
    #  ),
    # path(
    #      'purchase/<int:pk>/update/', PurchaseUpdateView.as_view(),
    #      name='purchase-update'
    #  ),
    path(
         'purchase/<int:pk>/delete/', PurchaseDeleteView.as_view(),
         name='purchase-delete'
     ),

     path(
         'bank/<int:pk>/delete/', BankDeleteView.as_view(),
         name='bank-delete'
     ),

    path(
        'new-bank/',BankCreateView.as_view(),name='bank-create'
    ),
    path(
        'search/',
        PurchaseItemSearchListView.as_view(),
        name='purchase_item_search_list_view'
    ),
    # Sale URLs
    path('sales/', SaleListView.as_view(), name='saleslist'),
    path('sale/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
    path('new-sale/', SaleCreateView, name='sale-create'),
    path(
         'sale/<slug:slug>/delete/', SaleDeleteView.as_view(),
         name='sale-delete'
     ),

     path('bank/export/', export_bank_to_excel, name='bank-export'),

    # Sales and purchases export
    path('sales/export/', export_sales_to_excel, name='sales-export'),
    path('purchases/export/', export_purchases_to_excel,
         name='purchases-export'),
    path('search-suggestions-purchase/', search_suggestions_purchase, name='search-suggestions-purchase'),
    # path('purchase_item_search_list_view/', purchase_item_search_list_view, name='purchase_item_search_list_view'),
    # path('add_customer/', add_customer, name='add_customer'),
    path('customers/', customer_search, name='customer_search'),
    path('customers/create/', customer_create, name='customer_create'),
    path('vendors/', vendor_search, name='vendor_search'),
    path('vendors/create/', vendor_create, name='vendor_create'),


]

# Static media files configuration for development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
