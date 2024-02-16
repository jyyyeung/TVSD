from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request) -> HttpResponse:
    return render(request, "pages/index.html", {})


def settings(request) -> HttpResponse:
    return render(request, "pages/settings.html", {})
