"""
Models for the tvsd_ui app.
"""

from django.db import models


class SearchSession(models.Model):
    """Stores search session data"""

    session_id = models.CharField(max_length=100, unique=True)
    query = models.CharField(max_length=200)
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"Search for '{self.query}' ({self.session_id})"


class SearchResult(models.Model):
    """Stores individual search results"""

    session = models.ForeignKey(
        SearchSession, on_delete=models.CASCADE, related_name="results"
    )
    index = models.IntegerField()
    title = models.CharField(max_length=200)
    note = models.TextField(blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    source_name = models.CharField(max_length=100)
    details_url = models.URLField(max_length=500)
    poster_url = models.URLField(max_length=500, blank=True, null=True)
    data = models.JSONField(blank=True, null=True)  # For any additional data

    def __str__(self) -> str:
        return f"{self.title} ({self.index})"


class SearchResultEpisode(models.Model):
    """Stores episodes for search results"""

    result = models.ForeignKey(
        SearchResult, on_delete=models.CASCADE, related_name="episodes"
    )
    number = models.IntegerField()
    title = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"Episode {self.number}: {self.title}"
