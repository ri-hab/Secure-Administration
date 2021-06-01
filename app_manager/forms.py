# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import Q


User = get_user_model()
################################################################################
            #####################Admin forms#####################
################################################################################
class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('type','username')

    def clean_email(self): 
        email = self.cleaned_data.get('email')
        if not email.endswith("3s.com.tn"):
            raise forms.ValidationError("Email address must end with: 3s.com.tn")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords must match")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = username.lower()
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("username is already taken!! try something else !!")
        return username

    def clean_Phone(self):
        Phone = self.cleaned_data.get('Phone')
        qs = User.objects.filter(Phone=Phone)
        if qs.exists():
            raise forms.ValidationError("Phone is already taken!! try something else !!")
        return Phone

    def clean_first_last_name(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        first_name = first_name.capitalize()
        last_name = last_name.upper()
        return first_name, last_name

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()
    class Meta:
        model = User
        fields = ('email','type')
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith("3s.com.tn"):
            raise forms.ValidationError("Email address must end with: 3s.com.tn")
        return email


    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = username.lower()
        email = self.cleaned_data.get('email')
        print(email)
        qs = User.objects.filter(Q(username=username) & ~Q(email=email))
        print(qs)
        # qs1 = User.objects.filter(email!=email)
        # print(qs1)
        if qs.exists() and email not in qs:
            raise forms.ValidationError("username is already taken!! try something else !!")
        return username

    def clean_Phone(self):
        Phone = self.cleaned_data.get('Phone')
        email = self.cleaned_data.get('email')
        print(email)
        qs = User.objects.filter(Q(Phone=Phone) & ~Q(email=email))
        print(qs)
        # qs1 = User.objects.filter(email!=email)
        # print(qs1)
        if qs.exists() and email not in qs:
            raise forms.ValidationError("Phone is already taken!! try something else !!")
        return Phone

    def clean_first_last_name(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        first_name = first_name.capitalize()
        last_name = last_name.upper()
        return first_name, last_name
################################################################################
            #####################Register form#####################
################################################################################

class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField()
    password2 = forms.CharField()
    class Meta:
        model = User
        fields = ('email','type','first_name', 'last_name','Phone', 'username')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith("3s.com.tn"):
            raise forms.ValidationError("Email address must end with: 3s.com.tn")
        return email

    def clean_Phone(self):
        Phone = self.cleaned_data.get('Phone')
        qs = User.objects.filter(Phone=Phone)
        if qs.exists():
            raise forms.ValidationError("Phone is already taken!! try something else !!")
        return Phone


    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("username is already taken!! try something else !!")
        return username

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords must match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.active = False # send confirmation email via signals
        # obj = EmailActivation.objects.create(user=user)
        # obj.send_activation_email()
        if commit:
            user.save()
        return user

################################################################################
            #####################Login form#####################
################################################################################
class LoginForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField()
    class Meta:
        model = User
        fields = ['type',]

class OTPForm(forms.Form):
	otp = forms.IntegerField()
