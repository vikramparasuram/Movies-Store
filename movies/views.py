from decimal import Decimal

from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Movie, Review, Order
from .forms import ReviewForm


# ---------- LIST ----------
def movie_list(request):
    q = request.GET.get("q", "")
    movies = Movie.objects.all()
    if q:
        movies = movies.filter(Q(title__icontains=q))
    return render(request, "movies/list.html", {"movies": movies, "q": q})


# ---------- DETAIL (with reviews + cart box) ----------
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.all().order_by("-created_at")

    # Build cart summary from session
    cart = request.session.get("cart", {})  # { "movie_id": qty }
    items = []
    total = Decimal("0.00")
    for mid, qty in cart.items():
        m = Movie.objects.get(pk=int(mid))
        line_total = (m.price or Decimal("0.00")) * qty
        items.append({"movie": m, "qty": qty, "line_total": line_total})
        total += line_total

    # Handle new review submission
    if request.method == "POST":
        if not request.user.is_authenticated:
            # only allow logged-in users to post reviews
            return redirect("accounts:login")
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect("movies:detail", pk=movie.pk)
    else:
        form = ReviewForm()

    return render(
        request,
        "movies/detail.html",
        {
            "movie": movie,
            "reviews": reviews,
            "form": form,
            "items": items,
            "total": total,
        },
    )


# ---------- ORDERS ----------
@login_required
def my_orders(request):
    orders = (
        request.user.orders.select_related()
        .prefetch_related("items__movie")
        .order_by("-created_at")
    )
    return render(request, "movies/orders.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "movies/order_detail.html", {"order": order})


# ---------- REVIEWS: edit/delete ----------
@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        return HttpResponseForbidden("You can only edit your own reviews.")

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("movies:detail", pk=review.movie.pk)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "movies/review_form.html",
        {"form": form, "movie": review.movie, "is_edit": True},
    )


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        return HttpResponseForbidden("You can only delete your own reviews.")

    if request.method == "POST":
        movie_pk = review.movie.pk
        review.delete()
        return redirect("movies:detail", pk=movie_pk)

    return render(request, "movies/review_confirm_delete.html", {"review": review})


def top_reviews(request):
    """
    Show top comments (highest-rated reviews across all movies),
    newest first on ties.
    """
    reviews = (
        Review.objects
        .select_related("movie", "user")
        .order_by("-rating", "-created_at")[:50]
    )
    return render(request, "movies/top_reviews.html", {"reviews": reviews})