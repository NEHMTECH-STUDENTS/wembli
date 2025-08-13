from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change-password'),
    path('delete-account/', views.delete_account, name='delete-account'),
    
    # User Profile URLs
    path('profile/', views.user_profile, name='user-profile'),
    path('profile/detail/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/user/', views.UserDetailView.as_view(), name='user-detail'),
    path('dashboard/', views.user_dashboard_data, name='user-dashboard'),
    
    # Address URLs
    path('addresses/', views.AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<int:address_id>/set-default/', views.set_default_address, name='set-default-address'),
    path('addresses/default/', views.get_default_address, name='get-default-address'),
    
    # Admin URLs
    path('users/', views.UserListView.as_view(), name='user-list'),
]