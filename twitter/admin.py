from django.contrib import admin, messages
from django.utils.translation import gettext as _, ngettext

from .models import TargetUser

from logging import getLogger

logger = getLogger(__name__)


@admin.register(TargetUser)
class TargetUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'twitter_id', 'username', 'name', 'created_at', 'updated_at')
    fields = ('id', 'uuid', 'twitter_id', 'username', 'name', 'created_at', 'updated_at')
    readonly_fields = ('id', 'uuid', 'created_at', 'updated_at')
    actions = ['update_data', 'clear_invalid']

    @admin.action(description='Update selected Target Users')
    def update_data(self, request, queryset):
        success = failed = 0
        for user in queryset:
            user: TargetUser
            try:
                user.update_data()
                user.save(update_fields=['name', 'username', 'twitter_id'])
                success += 1
            except ValueError:
                failed += 1
            except Exception as e:
                failed += 1
                logger.error(f'{type(e)} {e}')
                self.message_user(request, f'{type(e)} {e}', messages.ERROR)
        self.message_user(request, _(
            f'Success: {success}\n'
            f'Failed: {failed}\n'
            f'Total: {len(queryset)}\n'
        ), messages.SUCCESS)

    @admin.action(description='Clear selected Invalid Target Users')
    def clear_invalid(self, request, queryset):
        deleted = 0
        for user in queryset:
            user: TargetUser
            if not (user.twitter_id or user.username):
                user.delete()
                deleted += 1
        return self.message_user(request, ngettext(
            f'{deleted} Target User was deleted.',
            f'{deleted} Target Users were deleted.',
            deleted,
        ), messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        if isinstance(obj.username, str):
            obj.username = obj.username.lower()
        super().save_model(request, obj, form, change)
