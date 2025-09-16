from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.movie_list, name="list"),
    path("<int:pk>/", views.movie_detail, name="detail"),
    path("orders/", views.my_orders, name="orders"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("reviews/<int:pk>/edit/", views.review_edit, name="review_edit"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="review_delete"),
]
