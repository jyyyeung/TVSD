from django.contrib import admin

from web.tvsd_ui.models import SearchResult, SearchResultEpisode, SearchSession

# Register your models here.
admin.site.register(SearchSession)
admin.site.register(SearchResult)
admin.site.register(SearchResultEpisode)
