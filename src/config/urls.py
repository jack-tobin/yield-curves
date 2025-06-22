from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("src.apps.accounts.urls")),
    path("yield-curves/", include("src.apps.yield_curves.urls")),
    path("", lambda request: redirect("yield-curves/analysis/"), name="home"),
]


# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
