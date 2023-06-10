from django.utils.deconstruct import deconstructible
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.db import models
import os
import glob
from uuid import uuid4
from django import forms
from django.contrib.auth import get_user
import threading
from django.contrib.auth.models import AbstractUser


def get_current_request():
    return getattr(thread_local, 'request', None)


def path_and_rename(instance, filename):
    upload_to = os.path.join(os.path.dirname(
        __file__), 'static', 'images', 'db', 'known', instance.age_u)

    if not os.path.exists(upload_to):
        os.makedirs(upload_to)

    ext = filename.split('.')[-1]

    # Remove any occurrences of "../" in the filename
    filename = filename.replace('../', '')

    unknown_image = os.path.join(
        upload_to, f'{instance.age_u}_{instance.fname_u}_{instance.lname_u}_{instance.user}.{ext}')
    if os.path.exists(unknown_image):
        os.remove(unknown_image)

    uploaded_path = os.path.join(
        upload_to, f'{instance.age_u}_{instance.fname_u}_{instance.lname_u}_{instance.user}.{ext}')

    # Return the updated filename
    return uploaded_path


def rename(instance, filename):

    path = os.path.join(os.path.dirname(__file__), 'static',
                        'images', 'db', 'unknown', instance.age_f)

    if not os.path.exists(path):
        os.makedirs(path)

    ext = filename.split('.')[-1]

    # Remove any occurrences of "../" in the filename
    filename = filename.replace('../', '')

    unknown_image = os.path.join(
        path, f'{instance.age_f}_0.{ext}')
    if os.path.exists(unknown_image):
        os.remove(unknown_image)

    # Return the updated filename with the logged-in username
    return os.path.join(path, f'{instance.age_f}_0.{ext}')


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

AGE_CHOICES = (
    ('Child', 'Child'),
    ('Young', 'Young'),
    ('Middle', 'Middle'),
    ('Old', 'Old'),
)

SIGN_CHOICES = (
    ('Vision_Impairment', 'Vision_Impairment'),
    ('Blind', 'Blind'),
    ('Mental_health_disability', 'Mental_health_disability'),
    ('Intellectual_disability', 'Intellectual_disability'),
    ('Acquired_brain_injury', 'Acquired_brain_injury'),
    ('Autism_spectrum_disorder', 'Autism_spectrum_disorder'),
    ('Handless', 'Handless'),
    ('Feetless', 'Feetless'),
    ('Muscular_dystrophy', 'Muscular_dystrophy'),
    ('Cerebral_palsy', 'Cerebral_palsy'),
    ('Other', 'Other'),
)


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    birthday = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    email = models.EmailField(max_length=30, null=True)
    nid = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)


class LostPerson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    fname_u = models.CharField(max_length=100)
    lname_u = models.CharField(max_length=100)
    age_u = models.CharField(max_length=100, choices=AGE_CHOICES)
    sign_u = models.CharField(max_length=100, choices=SIGN_CHOICES)
    details_u = models.TextField()
    address_u = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=timezone.now)
    image_l = models.ImageField(
        upload_to=path_and_rename, null=True, blank=True)

    def __str__(self):
        return self.fname_u + ' ' + self.lname_u


class FindPerson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    age_f = models.CharField(max_length=100, choices=AGE_CHOICES)
    sign_f = models.CharField(max_length=100, choices=SIGN_CHOICES)
    image_f = models.ImageField(
        upload_to=rename, null=True, blank=True)

    def __str__(self):
        return self.age_f + ' ' + self.sign_f
