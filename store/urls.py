# Django core imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local app imports
from . import views
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ItemSearchListView,
    DeliveryListView,
    DeliveryDetailView,
    DeliveryCreateView,
    DeliveryUpdateView,
    DeliveryDeleteView,
    get_items_ajax_view,
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    HddCategoryListView,
    HddCategoryCreateView,
    HddCategoryDetailView,
    HddCategoryUpdateView,
    CatogaryItemSearchListView,
    search_suggestions,
    search_suggestions_product,
    add_processor1,
    create_processor,
    get_category_items,
    operativedashboard,
    upload_category_items,
    
)

# URL patterns
urlpatterns = [
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Product URLs
    path(
        'products/',
        ProductListView.as_view(),
        name='productslist'
    ),
    path(
        'product/<slug:slug>/',
        ProductDetailView.as_view(),
        name='product-detail'
    ),
    path(
        'new-product/',
        ProductCreateView.as_view(),
        name='product-create'
    ),
    path(
        'product/<slug:slug>/update/',
        ProductUpdateView.as_view(),
        name='product-update'
    ),
    path(
        'product/<slug:slug>/delete/',
        ProductDeleteView.as_view(),
        name='product-delete'
    ),

    # Item search
    path(
        'search/',
        ItemSearchListView.as_view(),
        name='item_search_list_view'
    ),

    path(
        'searchitem/',
        CatogaryItemSearchListView.as_view(),
        name='catogary_item_search_list_view'
    ),

    # Delivery URLs
    path(
        'deliveries/',
        DeliveryListView.as_view(),
        name='deliveries'
    ),
    path(
        'delivery/<slug:slug>/',
        DeliveryDetailView.as_view(),
        name='delivery-detail'
    ),
    path(
        'new-delivery/',
        DeliveryCreateView.as_view(),
        name='delivery-create'
    ),
    path(
        'delivery/<int:pk>/update/',
        DeliveryUpdateView.as_view(),
        name='delivery-update'
    ),
    path(
        'delivery/<int:pk>/delete/',
        DeliveryDeleteView.as_view(),
        name='delivery-delete'
    ),

    # AJAX view
    path(
        'get-items/',
        get_items_ajax_view,
        name='get_items'
    ),

    # Category URLs
    path(
        'categories/ram/',
        CategoryListView.as_view(),
        name='category-list'
    ),
    path(
        'categories/hdd/',
        HddCategoryListView.as_view(),
        name='category-list-Hdd'
    ),
    path(
        'categories/ram/<int:pk>/',
        CategoryDetailView.as_view(),
        name='category-detail'
    ),
    path(
        'categories/hdd/<int:pk>/',
        HddCategoryDetailView.as_view(),
        name='category-detail-hdd'
    ),
    path(
        'categories/create/ram',
        CategoryCreateView.as_view(),
        name='category-create'
    ),
    path(
        'categories/create/hdd',
        HddCategoryCreateView.as_view(),
        name='category-create-hdd'
    ),
    path(
        'categories/ram/<int:pk>/update/',
        CategoryUpdateView.as_view(),
        name='category-update'
    ),
    path(
        'categories/hdd/<int:pk>/update/',
        HddCategoryUpdateView.as_view(),
        name='category-update-hdd'
    ),
    path(
        'categories/<int:pk>/delete/',
        CategoryDeleteView.as_view(),
        name='category-delete'
    ),
    path('search-suggestions/', search_suggestions, name='search-suggestions'),
    path('search-suggestions-product/', search_suggestions_product, name='search-search-suggestions-product'),
    path('add-processor/', views.add_processor, name='add_processor'),
    path('add-ram/', views.add_ram, name='add_ram'),
    path('add-hdd/', views.add_hdd, name='add_hdd'),
    path('add-ssd/', views.add_ssd, name='add_ssd'),
    path('add-processor1/', add_processor1, name='add-processor1'),
    path('create-processor/', create_processor, name='create_processor'),
    # path('add-processor/', views.add_processor, name='add_processor')
    path('get-category-items/', get_category_items, name='get-category-items'),
    path('operative-dashboard/', operativedashboard, name='operative-dashboard'),
    path('upload-category-items/', upload_category_items, name='upload_category_items'),

]

# Static media files configuration for development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
