from django.db import models
from django.contrib.postgres.fields import CICharField

from extensions import twitter
from .managers import TargetUserManager as _TargetUserManager

import uuid


class BaseModel(models.Model):
    """BaseModel class"""

    uuid = models.UUIDField(
        verbose_name='UUID',
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name='Created at',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name='Updated at',
        auto_now=True,
    )

    class Meta:
        abstract = True


class TargetUser(BaseModel):
    objects = _TargetUserManager()
    twitter_id = models.CharField(
        verbose_name='Twitter ID',
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    username = CICharField(
        verbose_name='Username',
        max_length=15,
        unique=True,
        null=True,
        blank=True,
    )
    name = models.CharField(
        verbose_name='Name',
        max_length=50,
        null=True,
        blank=True,
    )

    def update_data(self):
        if data := (self.twitter_id or self.username):
            response = twitter.get_user_info(data)
            user_info = response.data
            self.name = user_info.name
            self.username = user_info.username
            self.twitter_id = int(user_info.id) or None
        else:
            raise ValueError('No data to update')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if isinstance(self.username, str):
            self.username = self.username.lower()
        super(TargetUser, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        if self.username:
            return self.username
        elif self.twitter_id:
            return str(self.twitter_id)
        return str(self.pk)

    class Meta:
        verbose_name = 'Target User'
        verbose_name_plural = 'Target Users'
