from django.db.models import manager


class TargetUserManager(manager.Manager):
    def twitter_user_ids(self):
        return self.values_list('twitter_id', flat=True)
