from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from marathons.forms import MarathonForm
from marathons.models import (
    Marathon,
    MarathonTicket
)
from movies.models import Movie



class MarathonListView(
    LoginRequiredMixin,
    ListView
):
    model = Marathon
    context_object_name = "marathons"

    def get_queryset(self):
        return (
            Marathon.objects
            .select_related("curator")
            .prefetch_related("movies", "participants")
        )


class MarathonCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView,
):
    model = Marathon
    form_class = MarathonForm

    def test_func(self):
        return self.request.user.role == self.request.user.Role.CURATOR

    def form_valid(self, form):
        movie_ids = self.request.POST.getlist("movies")
        if not movie_ids:
            form.add_error(None, "Select at least one movie")
            return self.form_invalid(form)

        marathon = form.save(commit=False)
        marathon.curator = self.request.user
        marathon.save()

        marathon.movies.set(movie_ids)

        return redirect("marathons:list")

    def get_success_url(self):
        return reverse("marathons:list")


class MarathonDetailView(
    LoginRequiredMixin,
    DetailView
):
    model = Marathon
    context_object_name = "marathon"

    def get_queryset(self):
        return (
            Marathon.objects
            .select_related("curator")
            .prefetch_related("movies", "participants")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        marathon = self.object

        context["is_joined"] = marathon.participants.filter(
            id=self.request.user.id
        ).exists()

        return context


class MarathonUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Marathon
    form_class = MarathonForm

    def test_func(self):
        return self.request.user == self.get_object().curator

    def form_valid(self, form):
        marathon = form.save(commit=False)
        marathon.save()

        movie_ids = self.request.POST.getlist("movies")
        marathon.movies.set(movie_ids)

        return redirect("marathons:detail", pk=marathon.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update"] = True
        context["marathon"] = self.object
        return context



class MarathonDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Marathon

    def test_func(self):
        return self.request.user == self.get_object().curator

    def get_success_url(self):
        return redirect("marathons:list").url


class JoinMarathonView(
    LoginRequiredMixin,
    View
):
    def post(
        self,
        request: HttpRequest,
        marathon_id: int,
    ) -> HttpResponse:
        marathon = get_object_or_404(Marathon, id=marathon_id)

        marathon.participants.add(request.user)

        MarathonTicket.objects.get_or_create(
            user=request.user,
            marathon=marathon,
        )

        return redirect("marathons:detail", pk=marathon.id)


class MarathonMovieSearchView(
    LoginRequiredMixin,
    View
):
    def get(
        self,
        request: HttpRequest,
    ) -> JsonResponse:
        q = request.GET.get("q", "").strip()

        if len(q) < 2:
            return JsonResponse([], safe=False)

        movies = (
            Movie.objects
            .filter(title__icontains=q)
            .only("id", "title", "year")
            .order_by("title", "year")[:20]
        )

        data = [
            {
                "id": movie.id,
                "title": movie.title,
                "year": movie.year,
            }
            for movie in movies
        ]

        return JsonResponse(data, safe=False)
