from django.conf import settings
from django.contrib.sites.models import Site


def domain(request):
  """
  Adds the currently active site object to the request
  """
  return {'site': Site.objects.get_current()}