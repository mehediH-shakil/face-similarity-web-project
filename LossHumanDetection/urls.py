from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from myapp import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.index, name='index'),
    path('home/', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    path('lost-person-register/', user_views.LostPersonRegister,
         name='lost-person-register'),
    path('find-lost-person/', user_views.find_lost_person,
         name='find-lost-person'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('similarity-score/', user_views.similarity_score_view,
         name='similarity_score'),
    path('all-post/', user_views.all_post, name='all-post'),
    path('single-post/', user_views.single_post, name='single-post'),
    path('profile/', user_views.profile, name='profile'),
    path('user-single-post/', user_views.user_single_post, name='user-single-post'),
    path('delete-post/<int:post_id>/',
         user_views.delete_post, name='delete-post'),
    path('edit-post/<int:post_id>/', user_views.edit_post, name='edit-post'),
    path('change-password/', user_views.change_password, name='change-password'),
    path('edit-profile/', user_views.edit_profile, name='edit-profile'),
]
