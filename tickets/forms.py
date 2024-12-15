from django import forms
from .models import Event, TicketType, Ticket
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Name",
    )

    class Meta:
        model = User
        fields = ['username', 'name', 'password1', 'password2']



class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'is_date_tbd', 'location', 'venmo_id', 'zelle_phone', 'bank_account_info']
        labels = {
            'name': 'Event Name',
            'description': 'Event Description',
            'is_date_tbd': 'Date To Be Determined',
            'date': 'Date and Time',
            'location': 'Event Location',
            'venmo_id': 'Venmo ID',
            'zelle_phone': 'Zelle Phone Number',
            'bank_account_info': 'Bank Account Details',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the event name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,  # Adjust height of the textarea
                'placeholder': 'Provide a brief description of the event',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',  # HTML5 datetime picker
            }),
            'is_date_tbd': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the location of the event',
            }),
            'venmo_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Venmo ID if necessary',
            }),
            'zelle_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Zelle phone number if necessary',
            }),
            'bank_account_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  # Adjust height of the textarea
                'placeholder': 'Provide bank account details if necessary',
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f"{field.label} <span class='text-danger'>*</span>") 



class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = ['name', 'price', 'currency', 'quantity_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'quantity_available': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Ticket Type Name',
            'price': 'Price',
            'currency': 'Currency',
            'quantity_available': 'Quantity Available',
        }


class TicketPurchaseForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        label="Confirm Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Ticket
        fields = ['first_name', 'last_name', 'email', 'payment_method', 'payment_identifier']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(
                    attrs={'class': 'form-control', 'id': 'payment-method'}, choices=['Venmo', 'Zelle', 'Bank Transfer']),
            'payment_identifier': forms.TextInput(
                    attrs={'class': 'form-control', 'id': 'payment-identifier'}),
            
        }

    def __init__(self, *args, **kwargs):
        payment_methods = kwargs.pop('payment_methods', {})
        super().__init__(*args, **kwargs)
        if payment_methods:
            self.fields['payment_method'].choices = [(key, value) for key, value in payment_methods.items()]


    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')

        if email != confirm_email:
            raise forms.ValidationError("Emails do not match.")
        
        return cleaned_data
