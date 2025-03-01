from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string

from tvsd.utils import get_sources_list
from web.tvsd_ui.components.config_form import ConfigForm
from web.tvsd_ui.components.search_bar import SearchBar

# from tvsd.actions import search_media_and_download
from tvsd.actions import list_shows_as_table, search_media, search_media_and_download
from tvsd.config import settings


# Create your views here.
def index_view(request) -> HttpResponse:
    if request.method == "POST":
        form = SearchBar(request.POST)

        if form.is_valid():
            # Do something with the form data
            print(form.cleaned_data)
            # search_media_and_download(form.cleaned_data["search"])

    return render(request, "tvsd_ui/index.html", {"form": SearchBar()})


def settings_view(request):
    if request.method == "POST":
        # Handle settings update
        settings.set("MEDIA_ROOT", request.POST.get("media_root"))
        settings.set("TEMP_ROOT", request.POST.get("temp_root"))
        settings.set("CREATE_MEDIA_ROOT", request.POST.get("create_media_root") == "on")
        settings.set("SOURCES", request.POST.getlist("sources"))
        messages.success(request, "Settings updated successfully")
        return redirect("tvsd_ui:settings")

    # Get current settings values
    context = {
        "media_root": settings.MEDIA_ROOT,
        "temp_root": settings.TEMP_ROOT,
        "create_media_root": settings.CREATE_MEDIA_ROOT,
        "sources": settings.SOURCES,
        "config_form": ConfigForm(),
    }
    return render(request, "tvsd_ui/settings.html", context)


def show_list(request):
    shows, count = list_shows_as_table(show_index=True)
    return render(request, "tvsd_ui/show_list.html", {"shows": shows, "count": count})


def search_view(request):
    results = None
    all_sources = get_sources_list()
    context = {
        "all_sources": all_sources,
    }
    if request.method == "POST":
        query = request.POST.get("query")
        sources = request.POST.getlist("sources")
        specials_only = request.POST.get("specials_only") == "on"
        messages.info(request, f"Searching for {query}")
        print(f"Searching for {query}")
        try:
            results = search_media(query, sources=sources, specials_only=specials_only)
            # print(f"Results: {results}")
            if results:
                messages.success(request, f'Found {len(results)} results for "{query}"')
            else:
                messages.warning(request, f'No results found for "{query}"')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            print(f"Error: {str(e)}")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = render_to_string(
                "tvsd_ui/search.html", {"results": results}, request=request
            )
            return HttpResponse(html)

    context["results"] = results
    return render(request, "tvsd_ui/search.html", context)


def home_view(request):
    return render(request, "tvsd_ui/home.html")


def show_list_view(request):
    shows, count = list_shows_as_table(show_index=True)
    return render(request, "tvsd_ui/shows.html", {"shows": shows, "count": count})


def download_view(request):
    if request.method == "POST":
        details_url = request.POST.get("details_url")
        try:
            # Initialize download with the details URL
            search_media_and_download(details_url, interactive=False)
            messages.success(request, "Download started successfully")
        except Exception as e:
            messages.error(request, f"Error starting download: {str(e)}")

    return redirect("tvsd_ui:shows")
