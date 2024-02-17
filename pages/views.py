from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from pages.components.config_form import ConfigForm
from pages.components.search_bar import SearchBar

# from tvsd.actions import search_media_and_download


# Create your views here.
def index_view(request) -> HttpResponse:
    if request.method == "POST":
        form = SearchBar(request.POST)

        if form.is_valid():
            # Do something with the form data
            print(form.cleaned_data)
            # search_media_and_download(form.cleaned_data["search"])

    return render(request, "pages/index.html", {"form": SearchBar()})


def settings_view(request) -> HttpResponse:
    if request.method == "POST":
        form = ConfigForm(request.POST)
        if form.is_valid():
            # Do something with the form data
            print(form.cleaned_data)
            settings.update(form.cleaned_data, validate=True)
            # TODO: Check if form is updated
    else:
        form = ConfigForm()
    return render(request, "pages/settings.html", {"form": form})
