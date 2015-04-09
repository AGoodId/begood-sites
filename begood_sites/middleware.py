from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers
from django.utils.translation import ugettext_lazy as _
from django.utils import translation


from models import SiteSettings
from utils import make_tls_property


_default_site_id = getattr(settings, 'SITE_ID', None)
_default_root_site_id = getattr(settings, 'ROOT_SITE_ID', None)
_default_language_code = getattr(settings, 'LANGUAGE_CODE', None)
SITE_ID = settings.__class__.SITE_ID = make_tls_property()
ROOT_SITE_ID = settings.__class__.ROOT_SITE_ID = make_tls_property()
LANGUAGE_CODE = settings.__class__.LANGUAGE_CODE = make_tls_property()
SITE_ID.value = _default_site_id
ROOT_SITE_ID.value = _default_root_site_id
LANGUAGE_CODE.value = _default_language_code


def generate_cache_key(domain):
  class_hash = hash(unicode(dir(Site)) + unicode(dir(SiteSettings)))
  return 'site:domain:%s:%s' % (class_hash, domain)


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
    ROOT_SITE_ID.value = site.settings.root_site_id
    LANGUAGE_CODE.value = site.settings.language_code or _default_language_code


class BasicAuthenticationMiddleware(object):
  """Adds basic authentication if set in the site settings"""

  def basic_challenge(self, realm=None):
    if realm is None:
      realm = getattr(settings, 'WWW_AUTHENTICATION_REALM', _('Restricted Access'))
    # TODO: Make a nice template for a 401 message?
    response =  HttpResponse(_('Authorization Required'), mimetype="text/plain")
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response

  def basic_authenticate(self, authentication, valid_username, valid_password):
    # Taken from paste.auth
    (authmeth, auth) = authentication.split(' ',1)
    if 'basic' != authmeth.lower():
      return False

    auth = auth.strip().decode('base64')
    username, password = auth.split(':',1)

    return username == valid_username and password == valid_password

  def process_request(self, request):
    # Get the configured username and password from the site settings
    site = Site.objects.get_current()
    valid_username = site.settings.basic_authentication_username
    valid_password = site.settings.basic_authentication_password

    if not valid_password or not valid_username:
      return None

    if 'HTTP_AUTHORIZATION' not in request.META:
      return self.basic_challenge()

    authenticated = self.basic_authenticate(request.META['HTTP_AUTHORIZATION'],
        valid_username, valid_password)

    if authenticated:
      return None

    return self.basic_challenge()


class LocaleMiddleware(object):
  """
  This is a very simple middleware that parses a request
  and decides what translation object to install in the current
  thread context.

  The language is chosen depending on the url path (eg. /en/)
  and checking if that is an installed language, otherwise it uses the
  default language.
  """

  def process_request(self, request):
    language = settings.LANGUAGE_CODE
    for lang_code, lang_name in settings.LANGUAGES:
      if request.path_info.startswith('/%s/' % str(lang_code)):
        language = lang_code
        break
    translation.activate(language)
    request.LANGUAGE_CODE = translation.get_language()

  def process_response(self, request, response):
    language = translation.get_language()
    translation.deactivate()

    patch_vary_headers(response, ('Accept-Language',))
    if 'Content-Language' not in response:
      response['Content-Language'] = language
    return response
