from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile

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
    
# from django.contrib.auth.forms import UserCreationForm
# from django import forms
# from django.contrib.auth.models import User
# from .models import CustomerProfile

# class CustomerRegistrationForm(UserCreationForm):
#     address = forms.CharField(widget=forms.TextInput, required=False)
#     phone_number = forms.CharField(max_length=15, required=False)
    
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         tailwind_classes = (
#             "block w-full rounded-md border-gray-300 shadow-sm "
#             "focus:border-indigo-500 focus:ring-indigo-500 px-3 py-2 shadow-sm sm:text-sm"
#         )

#         for field_name, field in self.fields.items():
#             field.widget.attrs.update({
#                 "class": tailwind_classes,
#                 "placeholder": field.label
#             })
            
    
#     def save(self, commit=True):
#         user = super().save(commit=commit)
#         address = self.cleaned_data.get('address')
#         phone_number = self.cleaned_data.get('phone_number')
        
#         if commit:
#             CustomerProfile.objects.create(
#                 user=user,
#                 address=address,
#                 phone_number=phone_number
                
#             )
#         return user