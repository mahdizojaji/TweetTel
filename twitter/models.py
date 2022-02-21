from django.db import models
from django.contrib.postgres.fields import CICharField

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
    twitter_id = models.BigIntegerField(
        verbose_name='Twitter ID',
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
