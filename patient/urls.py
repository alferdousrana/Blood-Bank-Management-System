from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('patientlogin/', LoginView.as_view(template_name='patient/patientlogin.html'), name='patientlogin'),
    path('patientlogout/', views.patient_logout_view, name='patientlogout'),
    path('patientsignup/', views.patient_signup_view, name='patientsignup'),
    path('make_request/', views.make_request_view, name='make_request'),
    path('my-request/', views.my_request_view, name='my-request'),
]