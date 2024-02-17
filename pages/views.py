from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from pages.components.config_form import ConfigForm


# Create your views here.
def index_view(request) -> HttpResponse:
    return render(request, "pages/index.html", {})


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
