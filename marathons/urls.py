from django.urls import path
from . import views

app_name = "marathons"

urlpatterns = [
    path("", views.marathon_list, name="list"),
    path("create/", views.create_marathon, name="create"),
    path("<int:pk>/", views.marathon_detail, name="detail"),
    path("<int:marathon_id>/join/", views.join_marathon, name="join"),
    path("<int:pk>/edit/", views.update_marathon, name="edit"),
    path("<int:pk>/delete/", views.delete_marathon, name="delete"),
]
