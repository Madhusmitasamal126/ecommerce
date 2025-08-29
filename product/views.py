from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Review
from account.models import Cart   # adjust if your Cart model lives in another app


def categories_page(request):
    all_categories = Category.objects.all()
    return render(request, 'categories.html', {'all_categories': all_categories})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    all_categories = Category.objects.all()

    return render(request, "product/category.html", {
        "category": category,
        "products": products,
        "all_categories": all_categories
    })



@login_required
def add_review(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment,
        )
        return redirect("get_product", slug=product.slug)  # redirect back to product page


def get_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    size = request.GET.get("size")
    color = request.GET.get("color")

    updated_price = product.get_product_price(size=size, color=color)
    related_products = Product.objects.exclude(id=product.id)[:4]

    context = {
        "product": product,
        "updated_price": updated_price,
        "related_products": related_products,
    }
    return render(request, "product/product.html", context)
@login_required
def checkout(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)

    context = {
        "cart_items": cart_obj.items.all(),
        "total_price": cart_obj.get_total(),
    }
    return render(request, "product/checkout.html", context)
def search_results(request):
    query = request.GET.get('q', '').strip()
    results = Product.objects.filter(pro_name__icontains=query) if query else []
    context = {
        'query': query,
        'results': results,
        'all_categories': Category.objects.all(),
    }
    return render(request, 'product/category_results.html', context)
