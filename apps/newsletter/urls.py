from django.urls import path
from .views import SubscribeView

app_name = 'newsletter'

urlpatterns = [
    path('', SubscribeView.as_view(), name='subscribe'),
    path('thanks/', SubscribeView.as_view(template_name='newsletter/thanks.html'), name='thanks'),
]
