from django.urls import URLPattern, path
from django.http import JsonResponse

from . import views

app_name = "tvsd_ui"

urlpatterns: list[URLPattern] = [
    path("", views.index_view, name="home"),
    path("search/", views.search_view, name="search"),
    path("shows/", views.show_list_view, name="shows"),
    path("settings/", views.settings_view, name="settings"),
    path("download/", views.download_view, name="download"),
    # path("api/episodes/", views.get_episodes, name="get_episodes"),
    path(
        "api/episodes/", views.get_episodes_index, name="get_episodes_index"
    ),
]
