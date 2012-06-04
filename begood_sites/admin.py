from django import forms
from django.contrib import admin
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from fields import MultiSiteField


class SiteModelAdmin(admin.ModelAdmin):

  def queryset(self, request):
    """
    Returns a Site filtered queryset for use in the Django admin change list
    """
    return self.model.on_site.get_query_set()

  def get_form(self, request, obj=None, **kwargs):
    # Need to store the object to use in formfield_for_dbfield
    self._object = obj
    return super(SiteModelAdmin, self).get_form(request, obj=obj, **kwargs)

  def formfield_for_dbfield(self, field, **kwargs):
    """
    Extends the default formfield_for_dbfield and makes sure the
    ``sites`` field is rendered as a ``FilteredSelectMultiple``
    widget and filtered with the sites the user has access to.
    """
    if isinstance(field, MultiSiteField):
      try:
        # Add any sites the user has access to
        user = kwargs['request'].user
        queryset = user.get_sites()
        if self._object is not None:
          # For existing objects, also add any sites that it's already published on
          queryset = queryset | self._object.sites.all()
          queryset = queryset.distinct()
      except KeyError:
        queryset = Site.objects.all()
      current_site = Site.objects.get_current()
      required = not field.blank
      return forms.ModelMultipleChoiceField(
        label=_('Sites'),
        queryset=queryset,
        initial={current_site.pk: 'selected'},
        required=required,
        widget=admin.widgets.FilteredSelectMultiple(_('sites'), False)
      )
    return super(SiteModelAdmin, self).formfield_for_dbfield(field, **kwargs)

