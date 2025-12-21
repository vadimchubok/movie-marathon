from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from .forms import MarathonForm
from .models import Marathon, MarathonTicket


@login_required
def marathon_list(request):
    marathons = Marathon.objects.all()
    return render(
        request,
        "marathons/marathon_list.html",
        {"marathons": marathons},
    )


@login_required
def create_marathon(request):
    if request.user.role != request.user.Role.CURATOR:
        raise PermissionDenied

    if request.method == "POST":
        form = MarathonForm(request.POST)
        movie_ids = request.POST.getlist("movies")

        if form.is_valid() and movie_ids:
            marathon = form.save(commit=False)
            marathon.curator = request.user
            marathon.save()
            marathon.movies.set(movie_ids)

            return redirect("marathons:list")
    else:
        form = MarathonForm()

    return render(
        request,
        "marathons/create_marathon.html",
        {"form": form}
    )

@login_required
def marathon_detail(request, pk):
    marathon = get_object_or_404(
        Marathon.objects
        .select_related("curator")
        .prefetch_related("movies", "participants"),
        pk=pk,
    )

    is_joined = marathon.participants.filter(id=request.user.id).exists()

    return render(
        request,
        "marathons/marathon_detail.html",
        {
            "marathon": marathon,
            "is_joined": is_joined,
        },
    )


@login_required
def update_marathon(request, pk):
    marathon = get_object_or_404(Marathon, pk=pk)

    if request.user != marathon.curator:
        raise PermissionDenied

    if request.method == "POST":
        form = MarathonForm(request.POST, instance=marathon)
        movie_ids = request.POST.getlist("movies")

        if form.is_valid():
            marathon = form.save()
            marathon.movies.set(movie_ids)  # 👈 ОБОВʼЯЗКОВО
            return redirect("marathons:detail", pk=marathon.id)
    else:
        form = MarathonForm(instance=marathon)

    return render(
        request,
        "marathons/create_marathon.html",
        {
            "form": form,
            "update": True,
            "marathon": marathon,  # 👈 ПОТРІБНО ДЛЯ JS
        }
    )


@login_required
def delete_marathon(request, pk):
    marathon = get_object_or_404(Marathon, pk=pk)

    if request.user != marathon.curator:
        raise PermissionDenied

    if request.method == "POST":
        marathon.delete()
        return redirect("marathons:list")

    return render(
        request,
        "marathons/confirm_delete.html",
        {"marathon": marathon},
    )


@login_required
def join_marathon(request, marathon_id):
    marathon = get_object_or_404(Marathon, id=marathon_id)

    marathon.participants.add(request.user)

    MarathonTicket.objects.get_or_create(
        user=request.user,
        marathon=marathon,
    )

    return redirect("marathons:detail", pk=marathon.id)
