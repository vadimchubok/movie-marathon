from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from movie_marathon.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", HomeView.as_view(), name="home"),

    path("movies/", include("movies.urls", namespace="movies")),
    path("marathons/", include("marathons.urls", namespace="marathons")),
    path("users/", include("users.urls", namespace="users")),

    path("login/", auth_views.LoginView.as_view(
        template_name="registration/login.html"
    ), name="login"),

    path("logout/", auth_views.LogoutView.as_view(template_name="registration/logout.html"), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
