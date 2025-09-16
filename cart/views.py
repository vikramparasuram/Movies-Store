from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from movies.models import Movie, Order, OrderItem  # we'll add Order models in step 2
from decimal import Decimal

CART_SESSION_KEY = "cart"  # { movie_id: quantity, ... }

def _get_cart(session):
    return session.setdefault('cart', {})

def cart_add(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    cart = _get_cart(request.session)
    cart[str(movie.id)] = cart.get(str(movie.id), 0) + 1
    request.session.modified = True
    messages.success(request, f"Added {movie.title} to cart.")
    return redirect("cart:detail")

def cart_clear(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    return redirect("cart:detail")

def cart_detail(request):
    cart = _get_cart(request.session)
    items = []
    total = Decimal("0.00")
    for mid, qty in cart.items():
        m = Movie.objects.get(pk=int(mid))
        line_total = (m.price or Decimal("0.00")) * qty
        items.append({"movie": m, "qty": qty, "line_total": line_total})
        total += line_total
    return render(request, "cart/detail.html", {"items": items, "total": total})

@login_required
def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:detail")


    order = Order.objects.create(user=request.user)
    for mid, qty in cart.items():
        movie = Movie.objects.get(pk=int(mid))
        OrderItem.objects.create(
            order=order,
            movie=movie,
            quantity=qty,
            price=movie.price,
        )

    # clear cart
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True

    messages.success(request, f"Order #{order.id} placed!")
    return redirect("movies:orders")  # we'll add this route next
