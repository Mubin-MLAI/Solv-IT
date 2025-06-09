from django import forms
from .models import Item, Delivery, Ssd,Hdd,Processor,Ram,catogaryitem




# class ItemForm(forms.ModelForm):
#     """
#     A form for creating or updating an Item in the inventory.
#     """
#     class Meta:
#         model = Item
#         fields = [
#             'name', 'serialno', 'make_and_models', 'processors', 'rams', 'hdds', 
#             'ssds', 'smps_status', 'motherboard_status', 'smps_replacement_description','motherboard_replacement_description' 
#         ]
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'serialno': forms.TextInput(attrs={'class': 'form-control'}),
#             'make_and_models': forms.TextInput(attrs={'class': 'form-control'}),
            
#             # Change the processor, ram, hdd, and ssd fields to text input
#             'processors': forms.SelectMultiple(attrs={'class': 'form-control'}),
#             # 'processor_qty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
#             'rams': forms.SelectMultiple(attrs={'class': 'form-control'}),
#             # 'ram_qty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
#             'hdds': forms.SelectMultiple(attrs={'class': 'form-control'}),
#             # 'hdd_qty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
#             'ssds': forms.SelectMultiple(attrs={'class': 'form-control'}),
#             # 'ssd_qty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            
#             # For SMPS, motherboard, and their statuses, keeping select dropdowns as is
#             'smps_status': forms.Select(attrs={'class': 'form-control'}),
#             'smps_replacement_description' : forms.TextInput(attrs={'class': 'form-control'}),
#             'motherboard_status': forms.Select(attrs={'class': 'form-control'}),
#             'motherboard_replacement_description' : forms.TextInput(attrs={'class': 'form-control'}),
#         }

            
            
#             # Quantity fields (NumberInput with min validation)
            
            
            
            
#             # Status fields as select dropdowns
        # labels = {
        #     'name': 'Item Name',
        #     'serialno': 'Serial Number',
        #     'make_and_models': 'Make and Model',
        #     'processors': 'Processor',
        #     # 'processor_qty': 'Processor Quantity',
        #     'rams': 'RAM',
        #     # 'ram_qty': 'RAM Quantity',
        #     'hdds': 'HDD',
        #     # 'hdd_qty': 'HDD Quantity',
        #     'ssds': 'SSD',
        #     # 'ssd_qty': 'SSD Quantity',
        #     'smps_status': 'SMPS Status',
        #     'smps_replacement_description': 'SMPS Description',
        #     'motherboard_status': 'Motherboard Status',
        #     'motherboard_replacement_description': 'Motherboard Description',
        # }


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
            'processors', 'rams', 'hdds', 'ssds',
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
            # 'smps_status': forms.Select(attrs={'class': 'form-control'}),
            # 'smps_replacement_description': forms.TextInput(attrs={'class': 'form-control'}),
            # 'motherboard_status': forms.Select(attrs={'class': 'form-control', }),
            # 'motherboard_replacement_description': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

    def save(self, commit=True):
        item = super().save(commit=False)
        if commit:
            item.save()
            # Set the unified components M2M field
            item.catogary_item_clone.set(
                list(self.cleaned_data['processors']) +
                list(self.cleaned_data['rams']) +
                list(self.cleaned_data['hdds']) +
                list(self.cleaned_data['ssds'])
            )
        return item


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
        fields = ['category', 'name', 'serial_no', 'quantity', 'unit_price']  # Added category field

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
            'category': 'Item Category',  # Dropdown label
            'name': 'Item Name',
            'serial_no': 'Serial Number',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
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
