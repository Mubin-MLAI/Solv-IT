from django import forms

from accounts.models import Vendor
from store.models import Item
from .models import Purchase,Bankaccount
from django_select2.forms import ModelSelect2Widget


from .models import ServiceBillItem

class ServiceBillItemForm(forms.ModelForm):
    class Meta:
        model = ServiceBillItem
        fields = ['customer', 'description', 'total_amount', 'total_tax', 'grand_total', 'item_name', 'qty', 'amount', 'tax_percent', 'tax_amt', 'amount_change']



class BootstrapMixin(forms.ModelForm):
    """
    A mixin to add Bootstrap classes to form fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


# class PurchaseForm(BootstrapMixin, forms.ModelForm):

#     """
#     A form for creating and updating Purchase instances.
#     """

#     class Meta:
#         model = Purchase
        
#         fields = [
#             'item',  'price', 'description', 'vendor',
#             'quantity', 'delivery_date', 'delivery_status', 'purchased_code'
#         ]

#         widgets = {
#             'delivery_date': forms.DateInput(
#                 attrs={
#                     'class': 'form-control',
#                     'type': 'datetime-local'
#                 }
#             ),
#             'description': forms.Textarea(
#                 attrs={'rows': 1, 'cols': 40}
#             ),
#             'quantity': forms.NumberInput(
#                 attrs={'class': 'form-control'}
#             ),
#             'delivery_status': forms.Select(
#                 attrs={'class': 'form-control'}
#             ),
#             'price': forms.NumberInput(
#                 attrs={'class': 'form-control'}
#             ),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # 🔽 Filter Item objects for purchased_code field
#         self.fields['purchased_code'].queryset = Item.objects.all()

#         # 🔽 Optional: Make dropdown labels more descriptive
#         self.fields['purchased_code'].label_from_instance = lambda obj: f"{obj.name} - {obj.purchased_code or 'N/A'}"

class BankForm(forms.ModelForm):
    class Meta:
        model = Bankaccount
        fields = [
            'account_name', 'opening_balance', 'as_of_date'
        ]
        widgets = {
            'account_name': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Enter Account Name',
                'style': 'text-transform: uppercase;'}),
            'opening_balance': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Enter Opening Balance',
                'style': 'text-transform: uppercase;'}),
            'as_of_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
        }


from django import forms


# Accept both sale_id and servicebill_id as optional fields for PaymentForm
class PaymentForm(forms.Form):
    sale_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    servicebill_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    amount_received = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)


from django import forms
from .models import Itempurchased, catogaryitempurchased


class ItemPurchasedForm(forms.ModelForm):
    processors = forms.ModelMultipleChoiceField(
        queryset=catogaryitempurchased.objects.filter(category='processor'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    rams = forms.ModelMultipleChoiceField(
        queryset=catogaryitempurchased.objects.filter(category='ram'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    hdds = forms.ModelMultipleChoiceField(
        queryset=catogaryitempurchased.objects.filter(category='hdd'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    ssds = forms.ModelMultipleChoiceField(
        queryset=catogaryitempurchased.objects.filter(category='ssd'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    

    class Meta:
        model = Itempurchased
        fields = [
            'name', 'serialno', 'make_and_models',
            'processors', 'rams', 'hdds', 'ssds', 'price', 'vendor_name', 'purchased_code'
            # 'smps_status', 'motherboard_status', 
            # 'smps_replacement_description', 'motherboard_replacement_description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Enter Product Name',
                'style': 'text-transform: uppercase;'}),
            'serialno': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Enter Serial No',
                'style': 'text-transform: uppercase;'}),
            'make_and_models': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Enter make and models',
                'style': 'text-transform: uppercase;'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Price',
                'aria-label': 'Price'    
            }),
            'vendor_name': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Purchased Code',
                'aria-label': 'Purchased Code',
                'required': 'required',               
            }),
            'purchased_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Purchased Code',
                'aria-label': 'Purchased Code',
                'required': 'required',                
            }),
            'smps_status': forms.Select(attrs={'class': 'form-control'}),
            'smps_replacement_description': forms.TextInput(attrs={'class': 'form-control'}),
            'motherboard_status': forms.Select(attrs={'class': 'form-control', }),
            'motherboard_replacement_description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is not None and qty < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return qty
        

    def save(self, commit=True):
        item = super().save(commit=False)
        if commit:
            item.save()
            # item.processors.set(self.cleaned_data['processors'])
            # item.rams.set(self.cleaned_data['rams'])
            # item.hdds.set(self.cleaned_data['hdds'])
            # item.ssds.set(self.cleaned_data['ssds'])
        return item

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor_name'].required = True  # ✅ Django-side required validation
        self.fields['purchased_code'].required = True