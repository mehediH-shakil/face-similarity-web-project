from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import LostPersonProfile
from django.contrib.auth.models import User
from .models import LostPerson, FindPerson


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, widget=forms.DateInput(attrs={'class': 'input--style-4'}))
    last_name = forms.CharField(max_length=30, widget=forms.DateInput(
        attrs={'class': 'input--style-4'}))
    birthday = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'class': 'input--style-4'}))
    gender = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')), widget=forms.DateInput(
        attrs={'class': 'input--style-4', 'type': 'ratio'}))
    email = forms.EmailField(widget=forms.DateInput(
        attrs={'class': 'input--style-4'}))
    nid = forms.CharField(max_length=30, widget=forms.DateInput(
        attrs={'class': 'input--style-4'}))
    address = forms.CharField(max_length=100, widget=forms.DateInput(
        attrs={'class': 'input--style-4'}))
    phone = forms.CharField(max_length=20, widget=forms.DateInput(
        attrs={'class': 'input--style-4'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birthday',
                  'gender', 'nid', 'address', 'phone', 'password1', 'password2')


class LostPersonForm(forms.ModelForm):
    class Meta:
        model = LostPerson
        fields = ['fname_u', 'lname_u', 'age_u',
                  'sign_u', 'details_u', 'address_u', 'image_l']


class FindLostPersonForm(forms.ModelForm):
    class Meta:
        model = FindPerson
        fields = ['age_f', 'sign_f', 'image_f']
