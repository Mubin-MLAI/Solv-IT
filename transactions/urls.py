# Django core imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local app imports
from .views import (
    PurchaseListView,
    PurchaseDetailView,
    PurchaseCreateView,
    PurchaseUpdateView,
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
    receive_payment
)

# URL patterns
urlpatterns = [
    # Purchase URLs
    path('receive-payment/', receive_payment, name='receive-payment'),
    path('cashbankListView/', cashbankListView.as_view(), name='cashbanklist'),
    path('purchases/', PurchaseListView.as_view(), name='purchaseslist'),
    path(
         'purchase/<slug:slug>/', PurchaseDetailView.as_view(),
         name='purchase-detail'
     ),
    path(
         'new-purchase/', PurchaseCreateView.as_view(),
         name='purchase-create'
     ),
    path(
         'purchase/<int:pk>/update/', PurchaseUpdateView.as_view(),
         name='purchase-update'
     ),
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
]

# Static media files configuration for development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
