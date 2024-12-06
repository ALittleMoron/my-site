from typing import Any

from django.db import models
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField


class PublishModel(models.Model):
    STATUS = Choices('draft', 'published')
    status = StatusField(verbose_name='Статус')
    status_changed = MonitorField(verbose_name='Статус изменен', monitor='status')

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        update_fields = kwargs.get('update_fields')
        if update_fields and 'status' in update_fields:
            kwargs['update_fields'] = set(update_fields).union({'status_changed'})

        super().save(*args, **kwargs)


class ModelWithName(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name
