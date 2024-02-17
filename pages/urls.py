from django.urls import URLPattern, path

from . import views

urlpatterns: list[URLPattern] = [
    path("", views.index_view, name="home"),
    path("settings", views.settings_view, name="settings"),
]
