from django.urls import path
from .views import AdOverviewView

app_name = 'ads'

urlpatterns = [
    path('', AdOverviewView.as_view(), name='overview'),
]
