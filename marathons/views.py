from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from marathons.forms import MarathonForm
from marathons.models import Marathon, MarathonTicket
from movies.models import Movie


class MarathonListView(LoginRequiredMixin, ListView):
    model = Marathon
    template_name = "marathons/marathon_list.html"
    context_object_name = "marathons"


class MarathonCreateView(LoginRequiredMixin,
                         UserPassesTestMixin,
                         CreateView
                         ):
    model = Marathon
    form_class = MarathonForm
    template_name = "marathons/create_marathon.html"

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


class MarathonDetailView(LoginRequiredMixin, DetailView):
    model = Marathon
    template_name = "marathons/marathon_detail.html"
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


class MarathonUpdateView(LoginRequiredMixin,
                         UserPassesTestMixin,
                         UpdateView
                         ):
    model = Marathon
    form_class = MarathonForm
    template_name = "marathons/create_marathon.html"

    def test_func(self):
        marathon = self.get_object()
        return self.request.user == marathon.curator

    def form_valid(self, form):
        marathon = form.save()
        movie_ids = self.request.POST.getlist("movies")
        marathon.movies.set(movie_ids)
        return redirect("marathons:detail", pk=marathon.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update"] = True
        context["marathon"] = self.object  # для JS
        return context


class MarathonDeleteView(LoginRequiredMixin,
                         UserPassesTestMixin,
                         DeleteView):
    model = Marathon
    template_name = "marathons/confirm_delete.html"

    def test_func(self):
        marathon = self.get_object()
        return self.request.user == marathon.curator

    def get_success_url(self):
        return redirect("marathons:list").url


@login_required
def join_marathon(request: HttpRequest,
                  marathon_id: int
                  ) -> HttpResponse:
    marathon = get_object_or_404(Marathon, id=marathon_id)

    marathon.participants.add(request.user)

    MarathonTicket.objects.get_or_create(
        user=request.user,
        marathon=marathon,
    )

    return redirect("marathons:detail", pk=marathon.id)

@login_required
def marathon_movie_search(request):
    q = request.GET.get("q", "").strip()

    if len(q) < 2:
        return JsonResponse([], safe=False)

    movies = (
        Movie.objects
        .filter(title__icontains=q)
        .order_by("title", "year")
        .only("id", "title", "year")[:20]  # ліміт для швидкості
    )

    data = [{"id": m.id, "title": m.title, "year": m.year} for m in movies]
    return JsonResponse(data, safe=False)
