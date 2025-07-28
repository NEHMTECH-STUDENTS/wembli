from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Category


def home(request):
    featured_products = Product.objects.filter(featured = True)
    categories = Category.objects.filter(is_active = True)
    latest_products = Product.objects.filter(available = True)
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'latest_products': latest_products
    }
    
    return render(request, 'home.html', context)



def about(request):
    return render(request, 'about.html')
