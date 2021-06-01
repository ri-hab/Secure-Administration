# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, request
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import CreateView, FormView
from .forms import RegisterForm, LoginForm, OTPForm
from app_admin.views import switcher_admin
from app_user.views import switcher_user
from app_auditor.views import switcher_auditor
from django.template.defaultfilters import slugify
from multiselectfield import MultiSelectField
from django.core.cache import cache
from twilio.rest import Client
from .utils import generate_otp
import random,os

from django.views import View
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import account_activation_token

User = get_user_model()


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'registration/signin.html'
    def form_valid(self, form):
        print("Validation succeeded!!")
        request = self.request
        email_form = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        type_form = form.cleaned_data.get('type')
        def selected(a):
            for x in a:
                return x
        type_selected = selected(type_form)

        user = authenticate(request,email=email_form, password=password)
        if user is not None:            
            if user.active:
                request.session['mobile'] = user.Phone
                request.session['user_id'] = user.id
                request.session['type_selected'] = type_selected
                g = generate_otp(user.Phone)
                return redirect('opt-verify')                                                                                                                                                                                                                                                                                                                                                                                   
            else:
                print("user not active !!!")
                return HttpResponseRedirect(reverse('notactive'))
        else:
            return HttpResponseRedirect(reverse('invalid'))
        return super(LoginView, self).form_invalid(form)


def send_otp(request):
    mobile_no = request.session.get('mobile')
    user_id = request.session.get('user_id')
    type_selected = request.session.get('type_selected')
    if request.method == 'POST':
        otp_form = OTPForm(request.POST)        
        if otp_form.is_valid() and mobile_no:
            entered_otp = otp_form.cleaned_data.get('otp')
            if cache.get(mobile_no):
                user = User.objects.get(id=user_id)
                if cache.get(mobile_no) == entered_otp:
                    l = login(request, user)
                    first_name = user.first_name
                    username_instance = user.username
                    cache.delete(mobile_no)
                    if list(user.type)[0] == "admin":
                        return HttpResponseRedirect(reverse("app_admin:switcher_admin", args=(slugify(username_instance),)))
                    elif list(user.type)[0] == "user":
                        return HttpResponseRedirect(reverse("app_user:switcher_user", args=(slugify(username_instance),)))
                    else:
                        return HttpResponseRedirect(reverse("app_auditor:switcher_auditor", args=(slugify(username_instance),)))
                else:
                    subject = "Invalid login credentials"
                    message = "Hi {},\n \nSomeone is trying to login to your account as an < {} >!\nWe hope that's you otherwise you must check your credentials.\n \n3S Jump Server Team".format(user.first_name, type_selected)
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [user.email, settings.EMAIL_HOST_USER]
                    send = send_mail(subject, message, from_email, to_list, fail_silently=False)
                    if send:
                        print("Mail sent successfully to the logged user!!!")
                    return HttpResponseRedirect(reverse('invalid'))
            return HttpResponseRedirect(reverse('invalid'))
    otp_form = OTPForm()
    return render(request,'send_otp/index.html', {'otp_form': otp_form})

def notactive(request):
    return render(request, "registration/notactive.html")

def invalid(request):
    return render(request, "registration/invalid.html")

def registered(request):
    return render(request, "registration/registered.html")



class RegisterViewUser(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'registration/signupUser.html', {'form': form})

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account
        print(request.POST)
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        print(password)
        type = request.POST['type']
        phone = request.POST['Phone']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 8:
                    messages.error(request, 'Password too short')
                    return render(request, 'registration/signupUser.html', context)

                user = User.objects.create_user(username=username, email=email, type=type, Phone=phone, password=password,first_name=first_name, last_name=last_name)
                #user.set_password(password)
                #user.is_active = False
                #user.save()
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage(
                    email_subject,
                    'Hi '+user.username + ', Please the link below to activate your account \n'+activate_url,
                    'noreply@semycolon.com',
                    [email],
                )
                print(email)
                email.send(fail_silently=False)
                messages.success(request, 'Account successfully created')

                subject = "Registration Succeeded"
                #first_name= form.cleaned_data.get('first_name')
                message = "Hi {},\n \nWe are glad that you have joined 3S Jump Server.\n \nThank you for the registration. \n \n3S Jump Server Team".format(username)
                from_email = settings.EMAIL_HOST_USER
                email = request.POST['email']
                to_list = [email, settings.EMAIL_HOST_USER]
                send = send_mail(subject, message, from_email, to_list, fail_silently=False)
                if send:
                    print("Mail sent successfully to the registred user!!!")
                    subject1 = "New Account Was Created"
                    message1 = "Hi,\n \nA new account was already created by < {} > with the following email address: {} !!!.\n \nPlease check if they are somebody who is allowed to register and mark their account active.\n \n3S Jump Server Team".format(username,email)
                    to_list1 = [settings.EMAIL_HOST_USER]
                    send1 = send_mail(subject1, message1, from_email, to_list1, fail_silently=False)
                    if send1:
                        print("Mail sent successfully to the admin!!!")
                    else:
                        print("We cannot send the mail to the admin :(")
                else:
                    print("We cannot send to mail to the registered user :(")



                return render(request, 'registration/signupUser.html')

        return render(request, 'registration/signupUser.html')



class RegisterViewAuditor(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'registration/signupAuditor.html', {'form': form})

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account
        print(request.POST)
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        print(password)
        type = request.POST['type']
        phone = request.POST['Phone']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 8:
                    messages.error(request, 'Password too short')
                    return render(request, 'registration/signupAuditor.html', context)

                user = User.objects.create_user(username=username, email=email, type=type, Phone=phone, password=password,first_name=first_name, last_name=last_name)
                #user.set_password(password)
                #user.is_active = False
                #user.save()
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage(
                    email_subject,
                    'Hi '+user.username + ', Please the link below to activate your account \n'+activate_url,
                    'noreply@semycolon.com',
                    [email],
                )
                print(email)
                email.send(fail_silently=False)
                messages.success(request, 'Account successfully created')

                subject = "Registration Succeeded"
                message = "Hi {},\n \nWe are glad that you have joined 3S Jump Server.\n \nThank you for the registration. \n \n3S Jump Server Team".format(username)
                from_email = settings.EMAIL_HOST_USER
                email = request.POST['email']
                to_list = [email, settings.EMAIL_HOST_USER]
                send = send_mail(subject, message, from_email, to_list, fail_silently=False)
                if send:
                    print("Mail sent successfully to the registred user!!!")
                    subject1 = "New Account Was Created"
                    message1 = "Hi,\n \nA new account was already created by < {} > with the following email address: {} !!!.\n \nPlease check if they are somebody who is allowed to register and mark their account active.\n \n3S Jump Server Team".format(username,email)
                    to_list1 = [settings.EMAIL_HOST_USER]
                    send1 = send_mail(subject1, message1, from_email, to_list1, fail_silently=False)
                    if send1:
                        print("Mail sent successfully to the admin!!!")
                    else:
                        print("We cannot send the mail to the admin :(")
                else:
                    print("We cannot send to mail to the registered user :(")



                return render(request, 'registration/signupAuditor.html')

        return render(request, 'registration/signupAuditor.html')





class RegisterViewAdmin(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'registration/signupAdmin.html', {'form': form})

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account
        print(request.POST)
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        print(password)
        type = request.POST['type']
        phone = request.POST['Phone']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 8:
                    messages.error(request, 'Password too short')
                    return render(request, 'registration/signupAdmin.html', context)

                user = User.objects.create_user(username=username, email=email, type=type, Phone=phone, password=password,first_name=first_name, last_name=last_name)
                #user.set_password(password)
                #user.is_active = False
                #user.save()
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage(
                    email_subject,
                    'Hi '+user.username + ', Please the link below to activate your account \n'+activate_url,
                    'noreply@semycolon.com',
                    [email],
                )
                print(email)
                email.send(fail_silently=False)
                messages.success(request, 'Account successfully created')

                subject = "Registration Succeeded"
                message = "Hi {},\n \nWe are glad that you have joined 3S Jump Server.\n \nThank you for the registration. \n \n3S Jump Server Team".format(username)
                from_email = settings.EMAIL_HOST_USER
                email = request.POST['email']
                to_list = [email, settings.EMAIL_HOST_USER]
                send = send_mail(subject, message, from_email, to_list, fail_silently=False)
                if send:
                    print("Mail sent successfully to the registred user!!!")
                    subject1 = "New Account Was Created"
                    message1 = "Hi,\n \nA new account was already created by < {} > with the following email address: {} !!!.\n \nPlease check if they are somebody who is allowed to register and mark their account active.\n \n3S Jump Server Team".format(username,email)
                    to_list1 = [settings.EMAIL_HOST_USER]
                    send1 = send_mail(subject1, message1, from_email, to_list1, fail_silently=False)
                    if send1:
                        print("Mail sent successfully to the admin!!!")
                    else:
                        print("We cannot send the mail to the admin :(")
                else:
                    print("We cannot send to mail to the registered user :(")



                return render(request, 'registration/signupAdmin.html')

        return render(request, 'registration/signupAdmin.html')





class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')
    # return render(request, 'home/register.html')
