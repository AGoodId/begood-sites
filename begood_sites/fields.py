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


# Make sure South migrations work
try:
  from south.modelsinspector import add_introspection_rules
  add_introspection_rules([], ["^begood_sites\.fields\.MultiSiteField"])
  add_introspection_rules([], ["^begood_sites\.fields\.SingleSiteField"])
except:
  pass
