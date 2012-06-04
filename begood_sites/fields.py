from django.db import models
from django.contrib.sites.models import Site


class MultiSiteField(models.ManyToManyField):

  def __init__(self, **kwargs):
    defaults = {
        'blank': False,
        }
    defaults.update(kwargs)
    super(MultiSiteField, self).__init__(Site, **defaults)


class SingleSiteField(models.ForeignKey):

  def __init__(self, **kwargs):
    super(SingleSiteField, self).__init__(Site, **kwargs)

