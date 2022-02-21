from django.contrib import admin

from .models import TargetUser


@admin.register(TargetUser)
class TargetUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'twitter_id', 'username', 'name', 'created_at', 'updated_at')
    fields = ('id', 'uuid', 'twitter_id', 'username', 'name', 'created_at', 'updated_at')
    readonly_fields = ('id', 'uuid', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if isinstance(obj.username, str):
            obj.username = obj.username.lower()
        super().save_model(request, obj, form, change)
