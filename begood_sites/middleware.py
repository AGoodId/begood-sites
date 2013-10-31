from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache


from utils import make_tls_property


_default_site_id = getattr(settings, 'SITE_ID', None)
_default_language_code = getattr(settings, 'LANGUAGE_CODE', None)
SITE_ID = settings.__class__.SITE_ID = make_tls_property()
LANGUAGE_CODE = settings.__class__.LANGUAGE_CODE = make_tls_property()


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
    site = cache.get(cache_key)
    if not site:
      # Cache was empty. Get the site from the DB
      try:
        site = Site.objects.select_related('settings').get(domain=domain)
      except Site.DoesNotExist:
        site = Site.objects.select_related('settings').get(id=_default_site_id)
      else:
        cache.set(cache_key, site, 5*60)

    # Set SITE_ID and LANGUAGE_CODE for this thread/request
    SITE_ID.value = site.id
    LANGUAGE_CODE.value = site.settings.language_code
    
