from django.contrib.auth import update_session_auth_hash
from PIL import Image
from django.http import HttpResponse
from django.core.paginator import Paginator

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm, LostPersonForm, FindLostPersonForm, ChangePasswordForm, UserProfileForm
from .models import LostPerson, FindPerson, UserProfile
import face_recognition
import sqlite3
from django.conf import settings
from django.urls import reverse
from django.core.files.base import ContentFile

import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K
from myapp.models import User

# env\Scripts\Activate.bat
# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

# Connect to the SQLite3 database
conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
cursor = conn.cursor()

# Execute the SQLite3 query
cursor.execute("SELECT * FROM myapp_lostperson")
rows = cursor.fetchall()
row_count = len(rows)

user_cursor = conn.cursor()

# Execute the SQLite3 query
user_cursor.execute("SELECT * FROM auth_user")
user_rows = user_cursor.fetchall()
user_rows_count = len(user_rows)
conn.close()

input_image_path = ''


def index(request):
    return render(request, 'index.html')


def home(request):
    context = {
        'data':  rows,
        'user_rows': user_rows
    }
    return render(request, 'home.html', context)


def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    fields = []
    for field in user_profile._meta.fields:
        field_name = field.verbose_name.capitalize()
        field_value = getattr(user_profile, field.name)
        fields.append((field_name, field_value))

    paginator = Paginator(rows, 5)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page,
        'user_rows': user_rows,
        'fields': fields
    }
    return render(request, 'profile.html', context)


def all_post(request):
    paginator = Paginator(rows, 2)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page,
        'user_rows': user_rows
    }
    return render(request, 'all_post.html', context)


root_path = {}


def user_single_post(request):
    value = request.GET.get('data')

    # Create a new SQLite connection for each request
    post_conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
    post_cursor = post_conn.cursor()

    # Execute the SQLite query
    post_cursor.execute(
        "SELECT * FROM myapp_lostperson WHERE id = ?", (value,))

    post_rows = post_cursor.fetchall()
    post_cursor.close()
    post_conn.close()

    post_filename = str(post_rows[0][8]).split('/')[-1]

    context = {
        'post_filename': post_filename,
        'post_rows':  post_rows,
        'user_rows': user_rows
    }
    return render(request, 'user_single_post.html', context)


def delete_post(request, post_id):
    post = get_object_or_404(LostPerson, id=post_id)
    if request.user == post.user:
        post.delete()

    return redirect('profile')


def edit_post(request, post_id):
    post = get_object_or_404(LostPerson, id=post_id)

    if post.user != request.user:
        return redirect('home')

    if request.method == "POST":
        post.fname_u = request.POST['fname_u']
        post.lname_u = request.POST['lname_u']
        post.age_u = request.POST['age_u']
        post.sign_u = request.POST['sign_u']
        post.details_u = request.POST['details_u']
        post.address_u = request.POST['address_u']

        image_l = request.FILES.get('image_l')
        if image_l:
            post.image_l = image_l

        # Save the updated post
        post.save()

        return redirect('profile')

    post_filename = str(post.image_l).split('/')[-1]
    context = {
        'post': post,
        'post_filename': post_filename

    }
    return render(request, 'edit_post.html', context)


def single_post(request):
    value = request.GET.get('data')

    # Create a new SQLite connection for each request
    post_conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
    post_cursor = post_conn.cursor()

    # Execute the SQLite query
    post_cursor.execute(
        "SELECT * FROM myapp_lostperson WHERE id = ?", (value,))

    post_rows = post_cursor.fetchall()
    post_cursor.close()
    post_conn.close()

    post_filename = str(post_rows[0][8]).split('/')[-1]

    context = {
        'post_filename': post_filename,
        'post_rows':  post_rows,
        'user_rows': user_rows
    }
    return render(request, 'single_post.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            birthday = form.cleaned_data['birthday']
            gender = form.cleaned_data['gender']
            nid = form.cleaned_data['nid']
            address = form.cleaned_data['address']
            phone = form.cleaned_data['phone']
            profile = UserProfile(user=user, first_name=first_name, last_name=last_name, email=email, birthday=birthday,
                                  gender=gender, nid=nid, address=address, phone=phone)
            profile.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'register.html', context)


@login_required(login_url='login')
def LostPersonRegister(request):
    if request.method == "POST":
        form = LostPersonForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            image = request.FILES['image_l']
            img = face_recognition.load_image_file(image)
            if face_recognition.face_locations(img):  # form.is_valid() and
                lost_person = form.save(commit=False)
                lost_person.user = request.user
                lost_person.save()
            else:
                messages.success(
                    request, 'There is no face detected in your image. So, Please try again with a proper image.')
                return redirect('lost-person-register')
        # messages.success(
        #     request, 'Thank you for adding! As soon as someone will Find him/her they will contact you.')
        # we can redirect to thank you page from here
        return redirect('home')
    else:
        return render(request, 'LostPersonRegister.html', {})


@login_required(login_url='find-lost-person')
def similarity_score_view(request):
    global input_image_path
    if input_image_path == "":
        return render(request, 'FindLostPerson.html')

    def load_image(image_path):
        image = Image.open(image_path)  # Load the image
        image = image.resize((28, 28))  # Resize the image to a desired size
        image = np.array(image)  # Convert the image to a NumPy array
        image = image / 255.0  # Normalize the pixel values between 0 and 1
        # Perform any other preprocessing steps as needed
        return image

    def contrastive_loss(y_true, y_pred):
        margin = 1.0
        return K.mean((1 - y_true) * K.square(y_pred) + y_true * K.square(K.maximum(margin - y_pred, 0)))

    # Register the contrastive_loss function with Keras
    tf.keras.utils.get_custom_objects()["contrastive_loss"] = contrastive_loss

    model_path = os.path.join(os.path.dirname(
        __file__), 'ML', 'siamese_model.h5')

    age = input_image_path.split('\\')[-2]
    known_images_folder = os.path.join(os.path.dirname(
        __file__), 'static', 'images', 'db', 'known', age)

    similarity_scores = {}

    model = keras.models.load_model(model_path)

    img1 = load_image(input_image_path)
    img1_input = img1.reshape((1, 28, 28, 3))

    similarity_scores = {}
    flag = "0"

    for filename in os.listdir(known_images_folder):
        img_path = os.path.join(known_images_folder, filename)
        img2 = load_image(img_path)
        img2_input = img2.reshape((1, 28, 28, 3))
        similarity_score = model.predict([img1_input, img2_input])[0][0]
        print(filename)

        similarity_images_folder = ""
        filename_age = filename.split('_')[0]
        filename_path = "myapp/static/images/db/known/" + filename_age + "/" + filename

        if similarity_score >= 0.8:
            flag = "1"
            formatted_similarity_score = "{:.2%}".format(similarity_score)
            similarity_scores[filename_path] = formatted_similarity_score
            print(formatted_similarity_score)

    context = {
        'flag': flag,
        'similarity_scores': similarity_scores,
        'data': rows,
        'user_rows': user_rows
    }
    return render(request, 'similarity_score.html', context)


@login_required(login_url='login')
def find_lost_person(request):
    global input_image_path
    if request.method == "POST":
        find_form = FindLostPersonForm(data=request.POST, files=request.FILES)
        age_f = request.POST['age_f']
        sign_f = request.POST['sign_f']
        if find_form.is_valid():
            image = request.FILES['image_f']
            img = face_recognition.load_image_file(image)
            if face_recognition.face_locations(img):  # form.is_valid() and
                find_form.save()
            else:
                messages.success(
                    request, 'There is no face detected in your image. So, Please try again with a proper image.')
                return redirect('find-lost-person')
        else:
            messages.success(request, 'There was an error in your form or there is no face in your image!'
                                      ' So, Please try again...')
            return render(request, 'FindLostPerson.html', {'age_f': age_f, 'sign_f': sign_f})

        input_image_path = os.path.join(os.path.dirname(
            __file__), 'static', 'images', 'db', 'unknown', str(age_f), str(age_f)+"_"+str(0) + "." +
            str(request.FILES['image_f']).split('.')[-1])
        return redirect(reverse('similarity_score'))
    else:
        return render(request, 'FindLostPerson.html', {})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            # Check if the old password matches the user's current password
            if not request.user.check_password(old_password):
                messages.error(request, 'Incorrect old password.')
            # Check if the new password and confirmation match
            elif new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                # Set the new password
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password successfully changed.')
                return redirect('profile')
    else:
        form = ChangePasswordForm()

    context = {
        'form': form
    }
    return render(request, 'change_password.html', context)


@login_required
def edit_profile(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            # Update user's first name, last name, and email
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form
    }
    return render(request, 'edit_profile.html', context)
