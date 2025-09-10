from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form for admin
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form for admin
    """
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with role management
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Display settings
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'organization',
        'phone_number',
        'is_active',
        'is_staff',
        'date_joined',
    )
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        'last_login',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'organization',
        'phone_number',
    )
    ordering = ('-date_joined',)

    # Fieldsets for editing users
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone_number',
                'organization',
            )
        }),
        ('Role & Permissions', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Fieldsets for adding users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'role',
                'password1',
                'password2',
            )
        }),
    )

    # Custom actions
    actions = ['activate_users', 'deactivate_users', 'make_pharma', 'make_hospital']

    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) were successfully activated.')
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) were successfully deactivated.')
    deactivate_users.short_description = "Deactivate selected users"

    def make_pharma(self, request, queryset):
        """Change selected users to Pharma role"""
        updated = queryset.update(role='pharma')
        self.message_user(request, f'{updated} user(s) were changed to Pharma role.')
    make_pharma.short_description = "Change to Pharma role"

    def make_hospital(self, request, queryset):
        """Change selected users to Hospital role"""
        updated = queryset.update(role='hospital')
        self.message_user(request, f'{updated} user(s) were changed to Hospital role.')
    make_hospital.short_description = "Change to Hospital role"
