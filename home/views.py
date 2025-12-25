from django.shortcuts import render
from product.models import Product, Category

# ---------------- Home Page ----------------
def index(request):
    categories = Category.objects.all()   # ✅ use same name as template
    latest_products = Product.objects.all().order_by('-id')[:8]  # latest 8 products
    
    context = {
        "categories": categories,          # ✅ matches template
        "latest_products": latest_products,
    }
    return render(request, "index.html", context)

# ---------------- Contact Page ----------------
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        # TODO: save to DB or send email
        print(name, email, message)
    return render(request, "contact.html")
