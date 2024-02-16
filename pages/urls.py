from django.urls import URLPattern, path

from . import views

urlpatterns: list[URLPattern] = [
    path("", views.index, name="home"),
    path("settings", views.settings, name="settings"),
]
