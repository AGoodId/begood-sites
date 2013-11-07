from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from django.utils.translation import ugettext as _

from models import SiteSettings
from fields import MultiSiteField
from reversion.admin import VersionAdmin

try:
  from begood.contrib.admin.widgets import DropDownSelectMultiple as DefaultSelectWidget
except ImportError:
  from django.contrib.admin.widgets import FilteredSelectMultiple as DefaultSelectWidget


class SiteModelAdmin(admin.ModelAdmin):

  def get_site_queryset(self, obj, user):
    queryset = user.get_sites()
    if obj is not None:
      # For existing objects, also add any sites that it's already published on
      queryset = queryset | obj.sites.all()
      queryset = queryset.distinct()
    return queryset

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
        queryset = self.get_site_queryset(self._object, user)
      except:
        queryset = Site.objects.all()
      current_site = Site.objects.get_current()
      required = not field.blank
      if 'widget' in kwargs:
        widget = kwargs['widget']
      else:
        widget = DefaultSelectWidget(_('sites'), False)
      return forms.ModelMultipleChoiceField(
        label=_('Sites'),
        queryset=queryset,
        initial={current_site.pk: 'selected'},
        required=required,
        widget=widget
      )
    return super(SiteModelAdmin, self).formfield_for_dbfield(field, **kwargs)


class SiteVersionAdmin(VersionAdmin):

  def _order_version_queryset(self, queryset):
    # Not the cleanest way to filter by site, but there was no better method to
    # override
    qs = super(SiteVersionAdmin, self)._order_version_queryset(queryset)
    return qs.filter(revision__versionsites__site_id=settings.SITE_ID)


class SiteSettingsInlineAdmin(admin.StackedInline):
  """
  Inline Admin class for site settings
  """
  model = SiteSettings
  verbose_name = _('site settings')
  verbose_name_plural = _('site settings')
  can_delete = False

  def get_formset(self, request, obj=None, **kwargs):
    # Store a reference to the current site
    self.obj = obj
    return super(SiteSettingsInlineAdmin, self).get_formset(request, obj=obj, **kwargs)

  def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    if db_field.name == "template_search" or db_field.name == "template_404":
      # Only show the templates from this site
      if self.obj and self.obj.id:
        kwargs["queryset"] = db_field.rel.to.objects.filter(sites__id=self.obj.id)
      else:
        kwargs["queryset"] = db_field.rel.to.objects.none()
    return super(SiteSettingsInlineAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class BeGoodSiteAdmin(SiteAdmin):
  """
  An admin class for the Site model with inline Site Settings
  """
  inlines = [SiteSettingsInlineAdmin]


# unregister default site admin
admin.site.unregister(Site)
# register new site admin
admin.site.register(Site, BeGoodSiteAdmin)
