# coding=utf-8

from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site


class Command(BaseCommand):
  args = '<name domain>'
  help = 'Add a new site with the specified name and domain. Returns the id of the new site.'

  def handle(self, *args, **options):
    name = args[0]
    domain = args[1]

    site = Site.objects.filter(name=name)
    if site.exists():
      raise CommandError('A Site with the name "%s" already exists' % name)

    site = Site.objects.filter(domain=domain)
    if site.exists():
      raise CommandError('A Site with the domain "%s" already exists' % domain)

    try:
      site = Site(name=name, domain=domain)
      site.save()
      print site.id
    except Exception, e:
      raise CommandError('Error when adding site: %s' % e)
    finally:
      connection.close()

