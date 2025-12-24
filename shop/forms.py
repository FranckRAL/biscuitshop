from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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
    wallet_number = forms.CharField(required=False)
    card_number = forms.CharField(required=False)
    expiry_date = forms.CharField(required=False)
    cvv = forms.CharField(required=False)
    paypal_email = forms.EmailField(required=False)
    
    
    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get("payment_method")

        if method in ["mvola", "orange", "airtel"]:
            if not cleaned_data.get("wallet_number"):
                self.add_error("wallet_number", "Wallet number is required for mobile money.")
        elif method == "card":
            if not cleaned_data.get("card_number"):
                self.add_error("card_number", "Card number is required.")
            if not cleaned_data.get("expiry_date"):
                self.add_error("expiry_date", "Expiry date is required.")
            if not cleaned_data.get("cvv"):
                self.add_error("cvv", "CVV is required.")
        elif method == "paypal":
            if not cleaned_data.get("paypal_email"):
                self.add_error("paypal_email", "PayPal email is required.")
        # COD requires no extra fields
        return cleaned_data
