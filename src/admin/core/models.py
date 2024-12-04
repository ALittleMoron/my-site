from typing import Any

from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField, MonitorField


class PublishModel(models.Model):
    STATUS = Choices('draft', 'published')
    status = StatusField(verbose_name='Статус')
    status_changed = MonitorField(verbose_name='Статус изменен', monitor='status')

    def save(self, *args: Any, **kwargs: Any) -> None:
        update_fields = kwargs.get('update_fields', None)
        if update_fields and 'status' in update_fields:
            kwargs['update_fields'] = set(update_fields).union({'status_changed'})

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class ModelWithName(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True
