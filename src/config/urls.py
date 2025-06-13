from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from src.apps.yield_curves.views import analysis_list

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("src.apps.accounts.urls")),
    path("yield-curves/", include("src.apps.yield_curves.urls")),
    path("yield-curves/analysis", analysis_list, name="home"),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
