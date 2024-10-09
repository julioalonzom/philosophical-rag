from django.urls import path
from .views import QueryView, create_checkout_session, stripe_webhook, login_view

urlpatterns = [
    path('query/', QueryView.as_view(), name='query'),
    path('create-checkout-session/', create_checkout_session, name='create-checkout-session'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('login/', login_view, name='login'),
]