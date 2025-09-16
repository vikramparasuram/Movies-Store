
from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("add/<int:pk>/", views.cart_add, name="add"),
    path("clear/", views.cart_clear, name="clear"),
    path("checkout/", views.checkout, name="checkout"),
]
