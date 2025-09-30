from django.urls import path
from .views import (
    PaymentAndOrderCreateView, 
    PaymentInitiateView, 
    payment_webhook, 
    payment_success,
    PaymentVerifyView  # Add this import
)

app_name = 'payments'

urlpatterns = [
    path('create-order/', PaymentAndOrderCreateView.as_view(), name='create-order'),
    path('initiate-payment/', PaymentInitiateView.as_view(), name='initiate-payment'),
    path('webhook/', payment_webhook, name='webhook'),
    path('verify/', PaymentVerifyView.as_view(), name='verify-payment'),  # Add this
    path('success/', payment_success, name='success'),
]

