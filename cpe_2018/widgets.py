from django.forms.widgets import Select, SelectMultiple
from django.forms.widgets import get_default_renderer
from django.utils.safestring import mark_safe


class SelectWithDisabled(SelectMultiple):
    """
    """

    def __init__(self, *args, **kwargs):
        self.src = kwargs.pop('src', {})
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        options = super(SelectWithDisabled, self).create_option(name, value, label, selected, index, subindex=None,
                                                          attrs=None)
        for k, v in self.src.items():
            options['attrs'][k] = v[options['value']]
        return options