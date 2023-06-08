from .views import register, login_view, test, index, home

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('test/', test, name='test'),
    path('index/', index, name='index'),
    path('home/', home, name='index')
]
