from django.urls import URLPattern, path

from . import views

app_name = "tvsd_ui"

urlpatterns: list[URLPattern] = [
    path("", views.index_view, name="home"),
    path("search/", views.search_view, name="search"),
    path("shows/", views.show_list_view, name="shows"),
    path("settings/", views.settings_view, name="settings"),
    path("download/", views.download_view, name="download"),
]
