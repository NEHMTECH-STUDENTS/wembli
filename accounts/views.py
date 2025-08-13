from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Profile, Address
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    ChangePasswordSerializer, ProfileSerializer, ProfileUpdateSerializer,
    AddressSerializer, AddressCreateSerializer, UserProfileSerializer
)


# Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create profile for user
        Profile.objects.create(user=user)
        # Create token for user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        # Delete the user's token
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        pass
    
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Update token
        try:
            token = Token.objects.get(user=user)
            token.delete()
            new_token = Token.objects.create(user=user)
            return Response({
                'message': 'Password changed successfully',
                'token': new_token.key
            }, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            new_token = Token.objects.create(user=user)
            return Response({
                'message': 'Password changed successfully',
                'token': new_token.key
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Profile Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)
    
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return ProfileUpdateSerializer
        return ProfileSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# Address Views
class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddressCreateSerializer
        return AddressSerializer


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        # If setting as default, unset other defaults
        if serializer.validated_data.get('is_default', False):
            Address.objects.filter(
                user=self.request.user, 
                is_default=True
            ).exclude(id=self.get_object().id).update(is_default=False)
        serializer.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_default_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        # Unset all other default addresses
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        # Set this address as default
        address.is_default = True
        address.save()
        
        serializer = AddressSerializer(address)
        return Response({
            'message': 'Default address updated successfully',
            'address': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Address.DoesNotExist:
        return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_default_address(request):
    try:
        address = Address.objects.get(user=request.user, is_default=True)
        serializer = AddressSerializer(address)
        return Response(serializer.data)
    except Address.DoesNotExist:
        return Response({'error': 'No default address found'}, status=status.HTTP_404_NOT_FOUND)


# User Management Views (for admin or extended functionality)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_data(request):
    """Get user dashboard data including orders, wishlist count, etc."""
    user = request.user
    
    # Import here to avoid circular imports
    from shop.models import Order, Wishlist
    
    # Get user stats
    total_orders = Order.objects.filter(user=user).count()
    pending_orders = Order.objects.filter(user=user, status='pending').count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    
    # Get recent orders
    from shop.serializers import OrderSerializer
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    recent_orders_data = OrderSerializer(recent_orders, many=True).data
    
    return Response({
        'user': UserProfileSerializer(user).data,
        'stats': {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'wishlist_count': wishlist_count,
        },
        'recent_orders': recent_orders_data
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    """Delete user account (soft delete by deactivating)"""
    password = request.data.get('password')
    
    if not password:
        return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not request.user.check_password(password):
        return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Deactivate user instead of deleting
    user = request.user
    user.is_active = False
    user.save()
    
    # Delete token
    try:
        token = Token.objects.get(user=user)
        token.delete()
    except Token.DoesNotExist:
        pass
    
    logout(request)
    return Response({'message': 'Account deactivated successfully'}, status=status.HTTP_200_OK)