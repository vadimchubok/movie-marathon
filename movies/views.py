from django.db.models import Avg, Count
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from movies.models import Movie, UserRating, Genre
from movies.models import Review

# Create your views here.
class MovieListView(ListView):
    model = Movie
    template_name = "movies/movies_list.html"
    context_object_name = "movies_list"
    paginate_by = 32

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["genres"] = Genre.objects.all()
        return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = "movies/movie_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect("login")

        # ⭐ User rating
        if "rating" in request.POST:
            value = int(request.POST.get("rating"))

            UserRating.objects.update_or_create(
                author=request.user,
                movie=self.object,
                defaults={"value": value},
            )

        # 💬 Review / Comment
        if "text" in request.POST:
            Review.objects.create(
                author=request.user,
                movie=self.object,
                text=request.POST.get("text"),
                is_review=request.POST.get("is_review") == "on",
            )

        return redirect("movies:movie_detail", pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # User rating
        if self.request.user.is_authenticated:
            context["user_rating"] = UserRating.objects.filter(
                author=self.request.user,
                movie=self.object,
            ).first()

        # Average rating
        context["avg_rating"] = self.object.rating.aggregate(
            avg=Avg("value")
        )["avg"]

        # Reviewer logic (TEMPORARY – template-level)
        reviewers = (
            Review.objects
            .values("author")
            .annotate(total=Count("id"))
            .filter(total__gte=10)
        )
        context["reviewer_ids"] = {r["author"] for r in reviewers}

        return context