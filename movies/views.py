from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from movies.models import Movie, UserRating, Genre, Review
from users.utils import update_user_status


class MovieListView(ListView):
    model = Movie
    template_name = "movies/movies_list.html"
    context_object_name = "movies_list"
    paginate_by = 32

    def get_queryset(self):
        movies_queryset = (
            Movie.objects
            .prefetch_related("genre")
            .annotate(avg_rating=Avg("rating__value"))
        )

        search_query = self.request.GET.get("q")
        if search_query:
            movies_queryset = movies_queryset.filter(title__icontains=search_query)

        selected_genres = self.request.GET.getlist("genre")
        if selected_genres:
            for genre_id in selected_genres:
                movies_queryset = movies_queryset.filter(genre__id=genre_id)

        year_filter = self.request.GET.get("year")
        if year_filter:
            try:
                year_filter = int(year_filter)
                movies_queryset = movies_queryset.filter(year=year_filter)
            except ValueError:
                pass

        # ↕️ SORTING
        sort_option = self.request.GET.get("sort")
        if sort_option == "title":
            movies_queryset = movies_queryset.order_by("title")
        elif sort_option == "year":
            movies_queryset = movies_queryset.order_by("-year")
        elif sort_option == "rating":
            movies_queryset = movies_queryset.order_by("-avg_rating")

        return movies_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["genres"] = Genre.objects.all()
        context["selected_genres"] = self.request.GET.getlist("genre")
        context["selected_sort"] = self.request.GET.get("sort", "")
        context["selected_year"] = self.request.GET.get("year", "")

        return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = "movies/movie_detail.html"

    COMMENTS_PER_PAGE = 10

    def post(self, request, *args, **kwargs):
        movie = self.get_object()

        if not request.user.is_authenticated:
            return redirect("login")

        # rating
        rating_value = request.POST.get("rating")
        if rating_value:
            UserRating.objects.update_or_create(
                author=request.user,
                movie=movie,
                defaults={"value": int(rating_value)},
            )

        # review
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

        # PRG pattern
        return redirect("movies:movie_detail", pk=movie.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()

        if self.request.user.is_authenticated:
            context["user_rating"] = UserRating.objects.filter(
                author=self.request.user, movie=movie
            ).first()

        context["avg_rating"] = UserRating.objects.filter(movie=movie).aggregate(
            avg=Avg("value")
        )["avg"]

        frequent_reviewers = (
            Review.objects
            .values("author")
            .annotate(total_reviews=Count("id"))
            .filter(total_reviews__gte=10)
            .values_list("author", flat=True)
        )
        context["reviewer_ids"] = set(frequent_reviewers)

        # ⭐ STAR RANGE
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


@require_GET
def movie_search(request):
    search_query = request.GET.get("q", "").strip()

    if len(search_query) < 2:
        return JsonResponse([], safe=False)

    movies = (
        Movie.objects
        .filter(title__icontains=search_query)
        .values("id", "title", "year")[:10]
    )

    return JsonResponse(list(movies), safe=False)
