from django.urls import path
from .views import check_license

urlpatterns = [
    path('licenses/<str:company_id>/', check_license, name='check_license'),
]