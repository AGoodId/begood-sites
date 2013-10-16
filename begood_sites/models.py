from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _


from reversion.models import Revision


from fields import *


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
  extra_html_head = models.TextField(_('Extra HTML-head'), blank=True)

  class Meta:
    verbose_name = _('site settings')
    verbose_name_plural = _('site settings')

  def __unicode__(self):
    return _('Settings for') + ' ' + self.site.name


def get_settings_property(site):
  if site and site.id:
    cache_key = 'sitesettings:%d' % site.id
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
    cache_key = 'sitesettings:%d' % instance.site_id
    cache.delete(cache_key)
  except:
    pass

@receiver(pre_delete, sender=Site, dispatch_uid='site_settings_signals')
@receiver(pre_save, sender=Site, dispatch_uid='site_settings_signals')
def clear_site_settings_cache_on_site_updated(sender, **kwargs):
  instance = kwargs['instance']
  try:
    cache_key = 'sitesettings:%d' % instance.id
    cache.delete(cache_key)
  except:
    pass
