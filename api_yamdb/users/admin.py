from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdminConfig(UserAdmin):
    search_fields = ('username',)
    list_filter = ('role',)
    ordering = ('username',)
    list_display = ('username', 'email', 'role', 'is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password',)}),
        ('Персональная информация', {'fields': ('first_name', 'last_name',
                                                'confirmation_code',)}),
        ('Разрешения', {'fields': ('is_staff', 'is_active', 'is_superuser',
                                   'role',)}),
        ('Остальное', {'fields': ('last_login', 'date_joined', 'bio',)})
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj.is_superuser:
            form.base_fields['role'].disabled = True
        return form


admin.site.register(User, UserAdminConfig)
