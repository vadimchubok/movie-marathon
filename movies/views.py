from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg, Count, QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView
)

from movies.models import (
    Movie,
    UserRating,
    Genre,
    Review
)
from users.utils import update_user_status


class MovieListView(ListView):
    model = Movie
    context_object_name = "movies_list"
    paginate_by = 32

    def get_queryset(self) -> QuerySet[Movie]:
        qs = Movie.objects.all()

        search_query = self.request.GET.get("q")
        if search_query:
            qs = qs.filter(title__icontains=search_query)

        selected_genres = self.request.GET.getlist("genre")
        if selected_genres:
            qs = qs.filter(genre__in=selected_genres)

        year_filter = self.request.GET.get("year")
        if year_filter and year_filter.isdigit():
            qs = qs.filter(year=int(year_filter))

        qs = qs.annotate(
            avg_rating=Avg("ratings__value")
        )

        sort_option = self.request.GET.get("sort")
        if sort_option == "title":
            qs = qs.order_by("title")
        elif sort_option == "year":
            qs = qs.order_by("-year")
        elif sort_option == "rating":
            qs = qs.order_by("-avg_rating")

        return qs.prefetch_related("genre").distinct()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["genres"] = Genre.objects.all()
        context["selected_genres"] = self.request.GET.getlist("genre")
        context["selected_sort"] = self.request.GET.get("sort", "")
        context["selected_year"] = self.request.GET.get("year", "")

        return context


class MovieDetailView(DetailView):
    model = Movie
    COMMENTS_PER_PAGE = 10

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponse:
        movie = self.get_object()

        if not request.user.is_authenticated:
            return redirect("login")

        rating_value = request.POST.get("rating")
        if rating_value:
            UserRating.objects.update_or_create(
                author=request.user,
                movie=movie,
                defaults={"value": int(rating_value)},
            )

        review_text = request.POST.get("text", "").strip()
        if review_text:
            is_review = request.POST.get("is_review") == "on"
            Review.objects.create(
                author=request.user,
                movie=movie,
                text=review_text,
                is_review=is_review,
            )
            update_user_status(request.user)

        return redirect("movies:movie_detail", pk=movie.pk)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        movie = self.get_object()

        if self.request.user.is_authenticated:
            context["user_rating"] = UserRating.objects.filter(
                author=self.request.user,
                movie=movie,
            ).first()

        context["avg_rating"] = UserRating.objects.filter(
            movie=movie
        ).aggregate(avg=Avg("value"))["avg"]

        frequent_reviewers = (
            Review.objects
            .values("author")
            .annotate(total_reviews=Count("id"))
            .filter(total_reviews__gte=10)
            .values_list("author", flat=True)
        )
        context["reviewer_ids"] = set(frequent_reviewers)
        context["rating_range"] = range(1, 11)

        reviews_queryset = (
            Review.objects
            .filter(movie=movie)
            .select_related("author")
            .order_by("-created_at")
        )

        paginator = Paginator(reviews_queryset, self.COMMENTS_PER_PAGE)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["reviews"] = page_obj.object_list
        context["page_obj"] = page_obj
        context["paginator"] = paginator
        context["is_paginated"] = page_obj.has_other_pages()

        return context


class ReviewDeleteView(
    LoginRequiredMixin,
    DeleteView
):
    model = Review

    def get_success_url(self):
        return reverse(
            "movies:movie_detail",
            kwargs={"pk": self.object.movie.pk},
        )

    def dispatch(self, request, *args, **kwargs):
        review = self.get_object()

        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        if review.author != request.user:
            raise PermissionDenied("You cannot delete this comment")

        return super().dispatch(request, *args, **kwargs)


class MovieSearchView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        search_query = request.GET.get("q", "").strip()

        if len(search_query) < 2:
            return JsonResponse([], safe=False)

        movies = (
            Movie.objects
            .filter(title__icontains=search_query)
            .values("id", "title", "year")[:10]
        )

        return JsonResponse(list(movies), safe=False)
