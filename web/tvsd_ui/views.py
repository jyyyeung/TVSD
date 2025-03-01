from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
import os
import uuid
import pickle
from django.conf import settings as django_settings

from tvsd.types.season import Season
from tvsd.utils import get_sources_list
from web.tvsd_ui.components.config_form import ConfigForm
from web.tvsd_ui.components.search_bar import SearchBar
import pickle

# from tvsd.actions import search_media_and_download
from tvsd.actions import (
    DownloadOptions,
    download_show,
    list_shows_as_table,
    search_media,
)
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
        sources = [source for source in sources if source != ""]
        messages.info(request, f"Searching for {query}")
        print(f"Searching for {query}")
        try:
            results = search_media(query, sources=sources)
            print(f"Results: {results}")
            # Store the index of each result for later reference
            for index, result in enumerate(results):
                result.index = index

            if results:
                # Generate a unique ID for this search session
                search_id = str(uuid.uuid4())
                request.session['search_id'] = search_id
                request.session['search_results_count'] = len(results)
                request.session['has_results'] = True

                # Save the results to a temporary file
                temp_dir = os.path.join(django_settings.BASE_DIR, 'temp_data')
                os.makedirs(temp_dir, exist_ok=True)

                pickle_path = os.path.join(temp_dir, f"{search_id}.pickle")
                with open(pickle_path, 'wb') as f:
                    pickle.dump(results, f)

                messages.success(request, f'Found {len(results)} results for "{query}"')
            else:
                request.session['has_results'] = False
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
            options = DownloadOptions(
                specials_only=request.POST.get("specials_only") == "on",
                episodes=request.POST.getlist("episodes"),
            )
            # Initialize download with the details URL
            download_show(details_url, options)
            messages.success(request, "Download started successfully")
        except Exception as e:
            messages.error(request, f"Error starting download: {str(e)}")

    return redirect("tvsd_ui:shows")


def get_episodes_index(request):
    # Get from prepare_download
    index = request.GET.get("index")
    if not index:
        return JsonResponse({"error": "Index parameter is required"}, status=400)

    try:
        index = int(index)
    except ValueError:
        return JsonResponse({"error": "Index must be an integer"}, status=400)

    # Check if we have results in the session
    if not request.session.get('has_results', False):
        return JsonResponse({"error": "No search results found in session"}, status=400)

    try:
        # Get the search ID from the session
        search_id = request.session.get('search_id')
        if not search_id:
            return JsonResponse({"error": "No search ID found in session"}, status=400)

        # Load the results from the temporary file
        temp_dir = os.path.join(django_settings.BASE_DIR, 'temp_data')
        pickle_path = os.path.join(temp_dir, f"{search_id}.pickle")

        if not os.path.exists(pickle_path):
            return JsonResponse({"error": "Search results file not found"}, status=400)

        with open(pickle_path, 'rb') as f:
            seasons = pickle.load(f)

        if index < 0 or index >= len(seasons):
            return JsonResponse({"error": f"Index {index} out of range"}, status=400)

        print(f"Seasons: {seasons}")
        season = seasons[index]
        season.fetch_details()
        episodes = [
            {"number": ep.episode_number, "title": ep.title} for ep in season.episodes
        ]
        print(f"Episodes: {episodes}")
        return JsonResponse({"episodes": episodes})
    except Exception as e:
        return JsonResponse(
            {"error": f"Error processing episodes: {str(e)}"}, status=500
        )
