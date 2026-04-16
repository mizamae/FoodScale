from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User 

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        exclude = ()

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        exclude=()

class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = User

    list_display = ("email",)
    ordering = ('email',)

    actions=['reset_password',]
    
    def reset_password(self, request, queryset):
        users_selected=queryset.count()
        for user in queryset:
            user.set_password('123')
            user.save()
            
    fieldsets = (
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        })
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin)