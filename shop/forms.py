from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re

class CustomerRegistrationForm(UserCreationForm):
    """Form for user registration with profile fields"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Email'
    }))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Username'
    }))
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirm Password'
        })
    )
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Phone (optional)'
    }))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Address (optional)',
        'rows': 3
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'address')

    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_phone_number(self):
        """Validate phone number format (Madagascar: 10-digit starting with 3, or with +261)"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove common separators
            cleaned_phone = re.sub(r'[\s\-\(\)]+', '', phone)
            # Madagascar phone: 3xxxxxxxxx or +2613xxxxxxxx
            if not re.match(r'^(\+261|0)?3\d{8}$', cleaned_phone):
                raise forms.ValidationError('Please enter a valid Madagascar phone number (e.g., 032xxxxxxxx or +2613xxxxxxxx)')
        return phone

    def save(self, commit=True):
        """Save user and return the instance"""
        user = super().save(commit=commit)
        if commit:
            user.refresh_from_db()
        return user
    
class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[
            ("mvola", "Mvola"),
            ("orange", "Orange Money"),
            ("airtel", "Airtel Money"),
            ("card", "Credit/Debit Card"),
            ("paypal", "PayPal"),
            ("cod", "Cash on Delivery"),
        ]
    )
    wallet_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Enter mobile money number',
        'maxlength': '15'
    }))
    card_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'XXXX XXXX XXXX XXXX',
        'maxlength': '19'
    }))
    expiry_date = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'MM/YY',
        'maxlength': '5'
    }))
    cvv = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'placeholder': 'XXX',
        'maxlength': '4'
    }))
    paypal_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'placeholder': 'your@paypal.com'
    }))
    
    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get("payment_method")

        if method in ["mvola", "orange", "airtel"]:
            wallet = cleaned_data.get("wallet_number")
            if not wallet:
                self.add_error("wallet_number", "Wallet number is required for mobile money.")
            elif not re.match(r'^(\+261|0)?3\d{8}$', re.sub(r'[\s\-\(\)]+', '', wallet)):
                self.add_error("wallet_number", "Invalid phone number format for mobile money.")
        elif method == "card":
            if not cleaned_data.get("card_number"):
                self.add_error("card_number", "Card number is required.")
            elif not re.match(r'^\d{13,19}$', re.sub(r'\s', '', cleaned_data.get("card_number", ""))):
                self.add_error("card_number", "Invalid card number.")
            if not cleaned_data.get("expiry_date"):
                self.add_error("expiry_date", "Expiry date is required.")
            elif not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', cleaned_data.get("expiry_date", "")):
                self.add_error("expiry_date", "Invalid expiry date format (MM/YY).")
            if not cleaned_data.get("cvv"):
                self.add_error("cvv", "CVV is required.")
            elif not re.match(r'^\d{3,4}$', cleaned_data.get("cvv", "")):
                self.add_error("cvv", "Invalid CVV.")
        # COD requires no extra fields
        return cleaned_data
