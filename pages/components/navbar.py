from django.shortcuts import redirect
from django_unicorn.components import UnicornView


class NavbarView(UnicornView):
    def redirect(self, url: str):

        return redirect(url)
