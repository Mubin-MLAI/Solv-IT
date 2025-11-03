from django import forms
from .models import Item, Delivery, Ssd,Hdd,Processor,Ram,catogaryitem


class ItemForm(forms.ModelForm):
    processors = forms.ModelMultipleChoiceField(
        queryset=catogaryitem.objects.filter(category='processor'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    rams = forms.ModelMultipleChoiceField(
        queryset=catogaryitem.objects.filter(category='ram'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    hdds = forms.ModelMultipleChoiceField(
        queryset=catogaryitem.objects.filter(category='hdd'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    ssds = forms.ModelMultipleChoiceField(
        queryset=catogaryitem.objects.filter(category='ssd'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    

    class Meta:
        model = Item
        fields = [
            'name', 'serialno', 'make_and_models',
            'processors', 'rams', 'hdds', 'ssds', 'price', 'purchased_code', 'note',
            'smps_status', 'motherboard_status', 
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
            'purchased_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Purchased Code',
                'aria-label': 'Purchased Code'
                
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

    
from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Select Excel file')



class RamForm(forms.ModelForm):
    """
    A form for creating or updating RAM details.
    """
    class Meta:
        model = Ram
        fields = ['name', 'serial_no', 'quantity', 'unit_price']  # Added new fields here
        
        # Widgets for custom form styling

        # widget={
        #     'name' : forms.TextInput(attrs={'class': 'form-control'}),
        #     'serial_no' : forms.TextInput(attrs={'class': 'form-control'}),
        #     'quantity' : forms.NumberInput(attrs={'class': 'form-control'}),
        #     'unit_price' : forms.NumberInput(attrs={'class': 'form-control'})
        # }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Ram Details',
                'aria-label': 'Ram Details'
            }),
            'serial_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Serial Number',
                'aria-label': 'Serial Number'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Quantity',
                'aria-label': 'Quantity'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Unit Price',
                'aria-label': 'Unit Price'
            }),
        }

        # Custom field labels
        labels = {
            'name': 'RAM',
            'serial_no': 'Serial Number',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
        }




class catogaryForm(forms.ModelForm):
    """
    A form for creating or updating item details such as SSD, Processor, RAM, or HDD.
    """
    class Meta:
        model = catogaryitem
        fields = ['category', 'name', 'serial_no', 'quantity', 'unit_price', 'purchase_lot_code']  # Added category field

        # Widgets for custom form styling
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
                'aria-label': 'Item Category'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Item Name',
                'aria-label': 'Item Name'
            }),
            'serial_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Serial Number or Leave Blank for SN : Solv-IT',
                'aria-label': 'Serial Number'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Quantity',
                'aria-label': 'Quantity'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Unit Price',
                'aria-label': 'Unit Price'
            }),

            'purchase_lot_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Purchase Code / Vendor Name',
                'aria-label': 'Purchase Code / Vendor Name'
            }),
        }

        # Custom field labels
        labels = {
            'category': 'Item Category',  # Dropdown label
            'name': 'Item Name',
            'serial_no': 'Serial Number',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
            'purchase_lot_code': 'Purchase Code / Vendor Name'
        }

    # Optionally, if you want to add extra validation for the category field
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category not in ['ssd', 'processor', 'hdd', 'ram']:
            raise forms.ValidationError("Invalid category selected.")
        return category


class HddForm(forms.ModelForm):
    """
    A form for creating or updating hdd.
    """
    class Meta:
        model = Hdd
        fields = ['name', 'serial_no', 'quantity', 'unit_price'] 
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Hdd Details',
                'aria-label': 'Hdd Details'
            }),
            'serial_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Serial Number',
                'aria-label': 'Serial Number'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Quantity',
                'aria-label': 'Quantity'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Unit Price',
                'aria-label': 'Unit Price'
            }),
        }

        # Custom field labels
        labels = {
            'name': 'HDD',
            'serial_no': 'Serial Number',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
        }

class ProcessorForm(forms.ModelForm):
    """
    A form for creating or updating Processor.
    """
    class Meta:
        model = Processor
        fields = ['name', 'serial_no', 'quantity', 'unit_price'] 
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Processor Details',
                'aria-label': 'Processor Details'
            }),
            'serial_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Serial Number',
                'aria-label': 'Serial Number'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Quantity',
                'aria-label': 'Quantity'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Unit Price',
                'aria-label': 'Unit Price'
            }),
        }

        # Custom field labels
        labels = {
            'name': 'PROCESSOR',
            'serial_no': 'Serial Number',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
        }

class SddForm(forms.ModelForm):
    """
    A form for creating or updating Sdd.
    """
    class Meta:
        model = Ssd
        fields = ['name', 'serial_no', 'quantity', 'unit_price'] 
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Sdd Details',
                'aria-label': 'Sdd Details'
            }),
            'serial_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Serial Number',
                'aria-label': 'Serial Number'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Quantity',
                'aria-label': 'Quantity'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Unit Price',
                'aria-label': 'Unit Price'
            }),
        }

        # Custom field labels
        labels = {
            'name': 'SDD',
            'serial_no': 'Serial Number',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
        }

# class M_2Form(forms.ModelForm):
#     """
#     A form for creating or updating M_2.
#     """
#     class Meta:
#         model = M_2
#         fields = ['name']
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter M.2 name',
#                 'aria-label': 'M.2 name'
#             }),
#             'model': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter model number ',
#                 'aria-label': 'model number'
#             }),
#             'capacity': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter capacity in GB',
#                 'aria-label': 'capacity in GB'
#             }),
#             'product code': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter M.2 product code ',
#                 'aria-label': 'M.2 product code'
#             }),
#         }
#         labels = {
#             'name': 'M.2',
#         }

# class NvmeForm(forms.ModelForm):
#     """
#     A form for creating or updating M_2.
#     """
#     class Meta:
#         model = Nvme
#         fields = ['name']
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter Nvme name',
#                 'aria-label': 'Nvme name'
#             }),
#             'model': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter model number ',
#                 'aria-label': 'model number'
#             }),
#             'capacity': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter capacity in GB',
#                 'aria-label': 'capacity in GB'
#             }),
#             'product code': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter Nvme product code ',
#                 'aria-label': 'Nvme product code'
#             }),
#         }
#         labels = {
#             'name': 'NVME',
#         }



class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            'item',
            'customer_name',
            'phone_number',
            'location',
            'date',
            'is_delivered'
        ]
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select item',
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery location',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Select delivery date and time',
                'type': 'datetime-local'
            }),
            'is_delivered': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'label': 'Mark as delivered',
            }),
        }
