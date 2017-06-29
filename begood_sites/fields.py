from django.db import models
from django.contrib.sites.models import Site
from django.forms.fields import *
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.widgets import *
from django.utils.encoding import smart_text, force_text
import copy
from django.utils.translation import ugettext_lazy as _

class MultiSiteField(models.ManyToManyField):


  def __init__(self, **kwargs):
    defaults = {
        'blank': False,
        }
    defaults.update(kwargs)
    if 'to' in defaults:
      del defaults['to']
    super(MultiSiteField, self).__init__(Site, **defaults)


class SingleSiteField(models.ForeignKey):

  def __init__(self, **kwargs):
    if 'to' in kwargs:
      del kwargs['to']
    super(SingleSiteField, self).__init__(Site, **kwargs)


# Make sure South migrations work
try:
  from south.modelsinspector import add_introspection_rules
  add_introspection_rules([], ["^begood_sites\.fields\.MultiSiteField"])
  add_introspection_rules([], ["^begood_sites\.fields\.SingleSiteField"])
except:
  pass

class RadioChoiceField(Field):
    widget = RadioSelect
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
    }

    def __init__(self, choices=(), required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):
        super(RadioChoiceField, self).__init__(required=required, widget=widget, label=label,
                                        initial=initial, help_text=help_text, *args, **kwargs)
        self.choices = choices

    def __deepcopy__(self, memo):
        result = super(RadioChoiceField, self).__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

    def to_python(self, value):
        "Returns a Unicode object."
        if value in validators.EMPTY_VALUES:
            return ''
        return smart_text(value)

    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        super(RadioChoiceField, self).validate(value)
        if value and not self.valid_value(value):
            raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})

    def valid_value(self, value):
        "Check to see if the provided value is a valid choice"
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == smart_text(k2):
                        return True
            else:
                if value == smart_text(k):
                    return True
        return False
