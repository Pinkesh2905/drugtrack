from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("dashboard.urls")),
    path('users/', include('users.urls')),
    path('inventory/', include('inventory.urls')),
    path('forecast/', include('ai_forecast.urls')),
    path('iot/', include('iot_mock.urls')),
]
