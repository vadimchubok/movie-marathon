from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("movies/", include("movies.urls", namespace="movies")),
    path("users/", include("users.urls", namespace="users")),
    path("marathons/", include("marathons.urls", namespace="marathons")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
