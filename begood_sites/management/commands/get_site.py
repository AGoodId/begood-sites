# coding=utf-8

from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site


class Command(BaseCommand):
  args = '<id_or_name>'
  help = 'Return the id, domain and name for a site'

  def handle(self, *args, **options):
    id_or_name = args[0]

    try:
      site = Site.objects.get(id=int(id_or_name))
    except (Site.DoesNotExist, ValueError):
      try:
        site = Site.objects.get(name=id_or_name)
      except Site.DoesNotExist:
        raise CommandError('No such site: %s' % id_or_name)

    print "%d %s %s" % (site.id, site.domain, site.name)

