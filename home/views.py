from django.shortcuts import render
from product.models import Product,Category





# Create your views here.
def index(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'index.html', context)

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        print(name, email, message)
    return render(request, "contact.html")
