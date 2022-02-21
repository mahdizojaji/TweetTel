from django.contrib import admin, messages

from .models import TargetUser

from logging import getLogger

logger = getLogger(__name__)


def update_data(modeladmin, request, queryset):
    for user in queryset:
        try:
            user.update_data()
            user.save(update_fields=['name', 'username', 'twitter_id'])
        except ValueError:
            user.delete()
        except Exception as e:
            messages.error(request, str(e))
            logger.error(f'{e}')


update_data.short_description = 'Update data selected Target Users'


@admin.register(TargetUser)
class TargetUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'twitter_id', 'username', 'name', 'created_at', 'updated_at')
    fields = ('id', 'uuid', 'twitter_id', 'username', 'name', 'created_at', 'updated_at')
    readonly_fields = ('id', 'uuid', 'created_at', 'updated_at')
    actions = [update_data, ]

    def save_model(self, request, obj, form, change):
        if isinstance(obj.username, str):
            obj.username = obj.username.lower()
        super().save_model(request, obj, form, change)
