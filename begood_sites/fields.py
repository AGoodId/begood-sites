from django.db import models
from django.contrib.sites.models import Site


class MultiSiteField(models.ManyToManyField):

  def __init__(self, **kwargs):
    defaults = {
        'blank': False,
        }
    defaults.update(kwargs)
    if 'to' in defaults:
      del defaults['to']
    super(MultiSiteField, self).__init__(Site, **defaults)


class SingleSiteField(models.ForeignKey):

  def __init__(self, **kwargs):
    if 'to' in kwargs:
      del kwargs['to']
    super(SingleSiteField, self).__init__(Site, **kwargs)


# Make sure South migrations work
try:
  from south.modelsinspector import add_introspection_rules
  add_introspection_rules([], ["^begood_sites\.fields\.MultiSiteField"])
  add_introspection_rules([], ["^begood_sites\.fields\.SingleSiteField"])
except:
  pass

import reversion
from reversion.models import Version, post_revision_commit
from models import VersionSite

# Add site meta data to Reversion revisions
def add_site_to_revision(sender, **kwargs):
  instances = kwargs['instances']
  revision = kwargs['revision']
  versions = kwargs['versions']
  sites = []

  for ver in versions:
    # Add any sites from the new version
    if 'sites' in ver.field_dict:
      sites.extend([int(s) for s in ver.field_dict['sites']])
    elif 'site' in ver.field_dict:
      sites.append(int(ver.field_dict['site']))
    # Add any sites from the previous version, so we can see that it has
    # moved
    try:
      available_versions = Version.objects.get_for_object(ver.object)
      prev_ver = available_versions.exclude(id=ver.id).order_by('-id')[0]
      if 'sites' in prev_ver.field_dict:
        sites.extend([int(s) for s in prev_ver.field_dict['sites']])
      elif 'site' in prev_ver.field_dict:
        sites.append(int(prev_ver.field_dict['site']))
    except IndexError:
      pass

  for site_id in set(sites):
    site = Site.objects.get(pk=site_id)
    # Add meta data didn't work, so do it manually
    vsite = VersionSite(revision=revision, site=site)
    vsite.save()

post_revision_commit.connect(add_site_to_revision, dispatch_uid="only_do_it_once")
