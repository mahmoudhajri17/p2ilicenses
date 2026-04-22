from django.urls import path
from .views import check_license

urlpatterns = [
path('licenses/check/', check_license, name='check_license')

]