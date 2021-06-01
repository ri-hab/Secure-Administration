# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from multiselectfield import MultiSelectField
from model_utils import Choices
from django.urls import reverse
import random
# from enum import Enum
 
class UserManager(BaseUserManager):
    def create_user(self, email,type, first_name="", last_name="", Phone="", username="", password=None, is_active=False, is_staff=False, is_admin=False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not type:
            raise ValueError('Users must have a type')
        if not username:
            raise ValueError('Users must have a username')
        if not Phone:
            raise ValueError('Users must have a Phone number')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            email=self.normalize_email(email),
            type = type,
            first_name = first_name if first_name == "" else first_name.capitalize(),
            last_name = last_name if last_name == "" else last_name.upper(),
            Phone = Phone ,
            username = username if username =="" else username.lower(),
            )
        user.set_password(password) #change user password
        user.active = is_active
        user.staff = is_staff
        user.admin = is_admin
        user.save(using=self._db)
        return user

    def create_staffuser(self,email,type = "admin",first_name="", last_name="",username='', Phone="", password=None):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            type,
            first_name,
            last_name,
            Phone,
            username,
            password=password,
            is_staff = True,
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, email,type = "admin",first_name="", last_name="", Phone="",username="", password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            type,
            first_name,
            last_name,
            Phone,
            username,
            password=password,
            is_staff=True,
            is_admin=True,
        )
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):

    email = models.EmailField(
        verbose_name = 'Email',
        default = 'user@3s.com.tn',
        max_length = 250,
        unique = True,
        blank= False,
    )

    USER_CATEGORY = Choices (
        ('admin', 'Administrator'),
        ('user', 'Privileged user'),
        ('auditor', 'Auditor'),
    )

    type = MultiSelectField(
    choices = USER_CATEGORY,
    verbose_name = 'Type',
    max_choices = 2,
    blank = False,
    default = USER_CATEGORY.user,
    )

    first_name = models.CharField(
        verbose_name = 'Firstname',
        max_length = 50,
        blank = True,
    )

    last_name = models.CharField(
        verbose_name = 'Lastname',
        max_length = 50,
        blank = True,
    )

    Phone = models.CharField(
        verbose_name = 'Phone',
        max_length = 12,
        blank = False,
    )

    username = models.CharField(
        verbose_name = 'username',
        max_length = 50,
        blank = False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'Phone'] #Email and password are required by default

    date_joined = models.DateTimeField(
    verbose_name = 'Date joined',
    default = timezone.now,
    # auto_now_add = True,
    )

    last_login = models.DateTimeField(
    verbose_name = 'Last Acess',
    auto_now = True,
    )

    image = models.ImageField(
    verbose_name = 'Profile picture',
    null = True,
    blank = True,
    upload_to = "app_manager",
    default='app_manager/default.PNG'
    )

    active = models.BooleanField(
    verbose_name = 'Active',
    default = True,
    )

    staff = models.BooleanField(     #The PAM admin has no access to Django Administration
    verbose_name = 'Staff',
    default = False,
    )

    admin = models.BooleanField(#if it's set to true, the admin user obtain full permissions
    verbose_name = 'Admin',
    default = False,
    )

    objects = UserManager()

    def get_ful_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email

    def __unicode__(self):
        return self.email

    def get_absolute_url(self):
        return reverse("app_user:switcher_user", kwargs={'username':self.username})

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active
    @property
    def type_user(self):
        return self.get_type_display()

class UserGroup(models.Model):
    name = models.CharField(
        max_length=40,
        verbose_name='User group name',
        blank=False,
        unique=True
    )
    user = models.ManyToManyField(
        User,
        related_name='users',
        verbose_name='users'
    )
    createdatetime = models.DateTimeField(
        default = timezone.now,
        verbose_name='Create time'
    )
    updatedatetime = models.DateTimeField(
        auto_created=True,
        auto_now=True,
        verbose_name='Update time'
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

