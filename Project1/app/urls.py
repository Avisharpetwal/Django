from django.urls import path
from .import views

urlpatterns = [
    path('app/',views.app1,name='app1'),

]
