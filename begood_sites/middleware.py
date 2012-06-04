from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache


from utils import make_tls_property


_default_site_id = getattr(settings, 'SITE_ID', None)
SITE_ID = settings.__class__.SITE_ID = make_tls_property()


def generate_cache_key(domain):
  return 'site:domain:%s' % domain


class DomainMiddleware(object):
  """Sets settings.SITE_ID based on request's domain"""
  def process_request(self, request):
    # Remove port number, if its given
    domain = request.get_host()
    if ':' in domain:
      domain = domain.split(':')[0]
    # Domains are case insensitive
    domain = domain.lower()
    # Check the cache
    cache_key = generate_cache_key(domain)
    site_id = cache.get(cache_key)
    if site_id:
      SITE_ID.value = site_id
    else:
      # Cache was empty. Get the site from the DB
      try:
        site = Site.objects.get(domain=domain)
      except Site.DoesNotExist:
        site_id = _default_site_id
      else:
        site_id = site.pk
        cache.set(cache_key, site_id, 5*60)
    # Set SITE_ID for this thread/request
    SITE_ID.value = site_id
    
