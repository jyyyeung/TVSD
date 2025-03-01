from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone
import datetime

from tvsd.utils import get_sources_list
from web.tvsd_ui.components.config_form import ConfigForm
from web.tvsd_ui.components.search_bar import SearchBar
from web.tvsd_ui.models import SearchSession, SearchResult, SearchResultEpisode

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
            results = search_media(query, sources=sources, is_interactive=False)
            print(f"Results: {results}")

            if results:
                # Create a new search session
                session_id = f"search_{timezone.now().timestamp()}"
                expires_at = timezone.now() + datetime.timedelta(hours=24)

                search_session = SearchSession.objects.create(
                    session_id=session_id,
                    query=query,
                    sources=sources,
                    expires_at=expires_at,
                )

                # Store each result in the database
                for index, result in enumerate(results):
                    search_result = SearchResult.objects.create(
                        session=search_session,
                        index=index,
                        title=result.title if hasattr(result, "title") else "",
                        note=result.note if hasattr(result, "note") else "",
                        year=result.year if hasattr(result, "year") else "",
                        source_name=(
                            result.source.__class__.__name__
                            if hasattr(result, "source")
                            else ""
                        ),
                        details_url=(
                            result.details_url if hasattr(result, "details_url") else ""
                        ),
                        poster_url=(
                            result.poster_url if hasattr(result, "poster_url") else ""
                        ),
                    )

                    # Store the result's details URL in the session for later use
                    if hasattr(result, "details_url"):
                        result.fetch_details()
                        # Store episodes if available
                        if hasattr(result, "episodes"):
                            for episode in result.episodes:
                                SearchResultEpisode.objects.create(
                                    result=search_result,
                                    number=(
                                        episode.episode_number
                                        if hasattr(episode, "episode_number")
                                        else 0
                                    ),
                                    title=(
                                        episode.title
                                        if hasattr(episode, "title")
                                        else ""
                                    ),
                                )

                # Store the session ID in the user's session
                request.session["search_session_id"] = session_id
                messages.success(request, f'Found {len(results)} results for "{query}"')
            else:
                request.session["search_session_id"] = None
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

    # Check if we have a search session ID in the user's session
    session_id = request.session.get("search_session_id")
    if not session_id:
        return JsonResponse({"error": "No active search session found"}, status=400)

    try:
        # Get the search session from the database
        search_session = SearchSession.objects.get(session_id=session_id)

        # Get the result with the specified index
        search_result = SearchResult.objects.get(session=search_session, index=index)

        # Get the episodes for this result
        episodes = SearchResultEpisode.objects.filter(result=search_result)

        # Format the episodes for the response
        episode_data = [
            {"number": episode.number, "title": episode.title} for episode in episodes
        ]

        return JsonResponse({"episodes": episode_data})
    except SearchSession.DoesNotExist:
        return JsonResponse({"error": "Search session not found"}, status=400)
    except SearchResult.DoesNotExist:
        return JsonResponse(
            {"error": f"Result with index {index} not found"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Error processing episodes: {str(e)}"}, status=500
        )
