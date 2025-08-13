from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Webmbli Ecommerce Adminstration"
admin.site.site_title = "Webmbli Ecommerce"
admin.site.index_title = "Webmbli Ecommerce Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

