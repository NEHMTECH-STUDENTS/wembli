from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Webmbli Ecommerce Adminstration"
admin.site.site_title = "Webmbli Ecommerce"
admin.site.index_title = "Webmbli Ecommerce Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
]

