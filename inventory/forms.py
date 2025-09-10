from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import DrugBatch


class DrugBatchForm(forms.ModelForm):
    class Meta:
        model = DrugBatch
        fields = ['name', 'manufacturer', 'batch_number', 'manufacture_date', 
                  'expiry_date', 'quantity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter drug name'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter manufacturer name'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique batch number'
            }),
            'manufacture_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity',
                'min': '1'
            }),
        }

    def clean_batch_number(self):
        batch_number = self.cleaned_data.get('batch_number')
        if batch_number:
            batch_number = batch_number.strip().upper()
            if DrugBatch.objects.filter(batch_number=batch_number).exists():
                raise ValidationError("A batch with this number already exists.")
        return batch_number

    def clean_manufacture_date(self):
        manufacture_date = self.cleaned_data.get('manufacture_date')
        if manufacture_date and manufacture_date > timezone.now().date():
            raise ValidationError("Manufacture date cannot be in the future.")
        return manufacture_date

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date <= timezone.now().date():
            raise ValidationError("Expiry date must be in the future.")
        return expiry_date

    def clean(self):
        cleaned_data = super().clean()
        manufacture_date = cleaned_data.get('manufacture_date')
        expiry_date = cleaned_data.get('expiry_date')

        if manufacture_date and expiry_date:
            if manufacture_date >= expiry_date:
                raise ValidationError("Expiry date must be after manufacture date.")
        
        return cleaned_data


class DrugVerificationForm(forms.Form):
    batch_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter batch number to verify',
            'required': True
        }),
        help_text="Enter the batch number to verify drug authenticity"
    )

    def clean_batch_number(self):
        batch_number = self.cleaned_data.get('batch_number')
        if batch_number:
            return batch_number.strip().upper()
        return batch_number


class DrugSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by drug name, manufacturer, or batch number',
        })
    )
    
    expiry_status = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('good', 'Good'),
            ('warning', 'Warning (90 days)'),
            ('expiring', 'Expiring Soon (30 days)'),
            ('expired', 'Expired'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    manufacturer = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by manufacturer',
        })
    )