from django.urls import path
from .views import assistant_index


app_name = "assistant_app"

urlpatterns = [
    path("", assistant_index, name="index"),
    # path("contact/", assistant_contact, name="contact"),
]