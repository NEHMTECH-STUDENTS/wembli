from django.urls import path
from . import views


app_name = 'shop'

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<slug:category_slug>/products/', views.ProductsByCategory.as_view(), name='products-by-category'),
    
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Cart URLs
    path('cart/', views.cart_detail, name='cart-detail'),
    path('cart/add/', views.add_to_cart, name='add-to-cart'),
    path('cart/items/<int:item_id>/update/', views.update_cart_item, name='update-cart-item'),
    path('cart/items/<int:item_id>/remove/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),
    
    # Order URLs
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', views.create_order, name='create-order'),
    
    # Review URLs
    path('products/<int:product_id>/reviews/', views.ProductReviewListView.as_view(), name='product-reviews'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    
    # Wishlist URLs
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle-wishlist'),
]