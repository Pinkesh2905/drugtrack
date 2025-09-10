from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("patient/", views.patient_dashboard, name="patient_dashboard"),
    path("hospital/", views.hospital_dashboard, name="hospital_dashboard"),
    path("pharma/", views.pharma_dashboard, name="pharma_dashboard"),
    path("regulator/", views.regulator_dashboard, name="regulator_dashboard"),
]
