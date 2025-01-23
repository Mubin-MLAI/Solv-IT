import django_filters
from .models import Item, catogaryitem


class ProductFilter(django_filters.FilterSet):
    """
    Filter set for Item model.
    """
    class Meta:
        model = Item
        fields = ['name', 'category', 'vendor']


class CategoryItemFilter(django_filters.FilterSet):
    """
    Filter set for CategoryItem model.
    """
    # Filter by category type
    category = django_filters.ChoiceFilter(
        choices=catogaryitem.CATEGORY_CHOICES, 
        label="Category"
    )
    
    # Filter by name of the item
    name = django_filters.CharFilter(
        lookup_expr='icontains',  # Use 'icontains' for case-insensitive partial match
        label="Item Name"
    )
    
    # Filter by serial number
    serial_no = django_filters.CharFilter(
        lookup_expr='icontains',
        label="Serial Number"
    )

    class Meta:
        model = catogaryitem  # Link to the CategoryItem model
        fields = ['category', 'name', 'serial_no']  # The fields to be filtered on
