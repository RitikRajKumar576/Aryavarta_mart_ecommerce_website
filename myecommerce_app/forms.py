from django import forms
from .models import Comingsoon, ContactUs, Contact, State
from django.contrib.auth import authenticate



# forms.py

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Enter your shipping address'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))

    PAYMENT_CHOICES = [
        ('credit-card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('cod', 'Cash on Delivery'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect)

    card_number = forms.CharField(max_length=16, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter card number (if applicable)'}))
    card_expiry = forms.DateField(required=False, widget=forms.DateInput(attrs={'placeholder': 'Enter card expiry date (if applicable)', 'type': 'month'}))
    cvv = forms.CharField(max_length=3, required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Enter CVV (if applicable)'}))
    
    def clean_card_number(self):
        if self.cleaned_data['payment_method'] == 'credit-card' and not self.cleaned_data.get('card_number'):
            raise forms.ValidationError('Card number is required for Credit/Debit Card payment.')
        return self.cleaned_data.get('card_number')

    def clean_cvv(self):
        if self.cleaned_data['payment_method'] == 'credit-card' and not self.cleaned_data.get('cvv'):
            raise forms.ValidationError('CVV is required for Credit/Debit Card payment.')
        return self.cleaned_data.get('cvv')







class ComingsoonForm(forms.ModelForm):
    class Meta:
        model = Comingsoon
        fields = ["header", "name", "image", "description", "price", "release_date", "status"]
        
        
        
# class ContactUsForm(forms.ModelForm):
#     class Meta:
#         model = ContactUs
#         fields = ['first_name', 'last_name', 'country_name', 'state_name', 'message']

#     def __init__(self, *args, **kwargs):
#         super(ContactUsForm, self).__init__(*args, **kwargs)

#         self.fields['country_name'].queryset = Contact.objects.all()
#         self.fields['state_name'].queryset = State.objects.none()  # Start empty

#         if 'country_name' in self.data:
#             try:
#                 country_id = int(self.data.get('country_name'))
#                 self.fields['state_name'].queryset = State.objects.filter(country_id=country_id)
#             except (ValueError, TypeError):
#                 pass



# class ContactUsForm(forms.ModelForm):
#     class Meta:
#         model = ContactUs
#         fields = ['first_name', 'last_name', 'country_name', 'state_name', 'message']

#     def __init__(self, *args, **kwargs):
#         super(ContactUsForm, self).__init__(*args, **kwargs)

#         # Correct Querysets
#         self.fields['country_name'].queryset = Contact.objects.all()  # ✅ Correct
#         self.fields['state_name'].queryset = State.objects.all()  # ✅ Correct

#         # Add placeholders
#         self.fields['first_name'].widget.attrs.update({'placeholder': 'Your name..'})
#         self.fields['last_name'].widget.attrs.update({'placeholder': 'Your last name..'})
#         self.fields['message'].widget.attrs.update({'placeholder': 'Write something..', 'style': 'height:170px'})


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['first_name', 'last_name', 'country_name', 'state_name', 'message']

    def __init__(self, *args, **kwargs):
        super(ContactUsForm, self).__init__(*args, **kwargs)

        self.fields['country_name'].queryset = Contact.objects.all()  # ✅ Correct
        self.fields['state_name'].queryset = State.objects.none()  # Start empty

        if 'country_name' in self.data:
            try:
                country_id = int(self.data.get('country_name'))
                self.fields['state_name'].queryset = State.objects.filter(country_id=country_id).order_by('state')
            except (ValueError, TypeError):
                pass
