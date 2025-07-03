from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Address


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('avatar', 'bio', 'phone', 'birth_date', 'address', 'city', 'postal_code', 'country', 'newsletter_subscription', 'email_notifications')


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fields = ('address_type', 'first_name', 'last_name', 'phone', 'address_line_1', 'city', 'postal_code', 'country', 'is_default')


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, AddressInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'newsletter_subscription', 'created_at']
    list_filter = ['newsletter_subscription', 'email_notifications', 'created_at', 'country']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'bio')
        }),
        ('Contact Information', {
            'fields': ('phone', 'birth_date')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscription', 'email_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_type', 'first_name', 'last_name', 'city', 'country', 'is_default']
    list_filter = ['address_type', 'is_default', 'country', 'created_at']
    search_fields = ['user__username', 'first_name', 'last_name', 'city', 'address_line_1']
    
    fieldsets = (
        ('User & Type', {
            'fields': ('user', 'address_type', 'is_default')
        }),
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        })
    )