from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
from django.core.serializers import SerializerDoesNotExist
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _


import reversion
from reversion.models import Revision, Version, post_revision_commit


from .fields import SingleSiteField


class VersionSite(models.Model):
  revision = models.ForeignKey(Revision, related_name="versionsites")
  site = SingleSiteField()

  objects = models.Manager()
  on_site = CurrentSiteManager()

  class Meta:
    unique_together = ("revision", "site")

  def __unicode__(self):
    return unicode(self.revision) +"<->"+ unicode(self.site)


class SiteSettings(models.Model):
  site = models.OneToOneField(Site, primary_key=True, related_name="settings")
  root_site = models.ForeignKey(Site, default=1, related_name="children")
  extra_html_head = models.TextField(_('Extra HTML-head'), blank=True)
  template_search = models.ForeignKey('begood.Template', verbose_name=_("search template"),
      blank=True, null=True, related_name='+')
  template_404 = models.ForeignKey('begood.Template', verbose_name=_("404 template"),
      blank=True, null=True, related_name='+')
  language_code = models.CharField(_('language'), max_length=10,
      choices=settings.LANGUAGES, default='sv')
  basic_authentication_username = models.CharField(_('username'), max_length=255, blank=True)
  basic_authentication_password = models.CharField(_('password'), max_length=255, blank=True)

  class Meta:
    verbose_name = _('site settings')
    verbose_name_plural = _('site settings')

  def __unicode__(self):
    return _('Settings for') + ' ' + self.site.name


def get_cache_key(site_id):
  class_hash = hash(unicode(dir(SiteSettings)))
  return 'sitesettings:%d:%d' % (class_hash, site_id)


def get_settings_property(site):
  if site and site.id:
    cache_key = get_cache_key(site.id)
    settings = cache.get(cache_key)
    if settings is None:
      settings = SiteSettings.objects.get_or_create(site=site)[0]
      cache.set(cache_key, settings, 24*60*60)
    return settings
  else:
    return None
Site.settings = property(get_settings_property)

@receiver(pre_delete, sender=SiteSettings, dispatch_uid='site_settings_signals')
@receiver(pre_save, sender=SiteSettings, dispatch_uid='site_settings_signals')
def clear_site_settings_cache_on_site_settings_updated(sender, **kwargs):
  instance = kwargs['instance']
  try:
    cache_key = get_cache_key(instance.site_id)
    cache.delete(cache_key)
  except:
    pass

@receiver(pre_delete, sender=Site, dispatch_uid='site_settings_signals')
@receiver(pre_save, sender=Site, dispatch_uid='site_settings_signals')
def clear_site_settings_cache_on_site_updated(sender, **kwargs):
  instance = kwargs['instance']
  try:
    cache_key = get_cache_key(instance.id)
    cache.delete(cache_key)
  except:
    pass

# Add site meta data to Reversion revisions
def add_site_to_revision(sender, **kwargs):
  instances = kwargs['instances']
  revision = kwargs['revision']
  versions = kwargs['versions']
  sites = []

  if revision.versionsites.exists():
    # If the sites are already set earlier, don't reset them here
    return

  for ver in versions:
    # Add any sites from the new version
    if 'sites' in ver.field_dict:
      sites.extend([int(s) for s in ver.field_dict['sites']])
    elif 'site' in ver.field_dict:
      sites.append(int(ver.field_dict['site']))
    # Add any sites from the previous version, so we can see that it has
    # moved
    try:
      available_versions = reversion.get_for_object_reference(ver.content_type.model_class(), ver.object_id)
      prev_ver = available_versions.exclude(id=ver.id).order_by('-id')[0]
      if 'sites' in prev_ver.field_dict:
        sites.extend([int(s) for s in prev_ver.field_dict['sites']])
      elif 'site' in prev_ver.field_dict:
        sites.append(int(prev_ver.field_dict['site']))
    except (IndexError, SerializerDoesNotExist):
      pass

  for site_id in set(sites):
    site = Site.objects.get(pk=site_id)
    # Add meta data didn't work, so do it manually
    vsite = VersionSite(revision=revision, site=site)
    vsite.save()

post_revision_commit.connect(add_site_to_revision, dispatch_uid="only_do_it_once")
