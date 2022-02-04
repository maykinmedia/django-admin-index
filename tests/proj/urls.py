from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.urls import re_path

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
]
