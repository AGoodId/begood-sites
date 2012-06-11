from django.db import models
from reversion.models import Revision
from django.contrib.sites.managers import CurrentSiteManager

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

