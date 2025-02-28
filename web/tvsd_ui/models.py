import os

from django.db import models

from tvsd.config import settings


class Show(models.Model):
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    begin_year = models.CharField(max_length=200)
    prefix = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    def relative_show_dir(self):
        return os.path.join(settings.SERIES_DIR, self.prefix)


class Season(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    begin_year = models.CharField(max_length=200)
    prefix = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Episode(models.Model):
    index = models.IntegerField()
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    begin_year = models.CharField(max_length=200)
    prefix = models.CharField(max_length=200)

    def __str__(self):
        return self.title
