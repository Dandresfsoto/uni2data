from crispy_forms.layout import *

class Stepper(LayoutObject):
    """

    """
    template = "crispy-forms/layout/stepper.html"

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.css_class = kwargs.pop('css_class', '')
        self.css_id = kwargs.pop('css_id', None)
        self.template = kwargs.pop('template', self.template)
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        fields = self.get_rendered_fields(form, form_style, context, template_pack, **kwargs)

        template = self.get_template_name(template_pack)
        return render_to_string(
            template,
            {'stepper': self, 'fields': fields, 'form_style': form_style}
        )


class StepInitial(LayoutObject):
    """

    """
    template = "crispy-forms/layout/step-initial.html"

    def __init__(self, title, *fields, **kwargs):
        self.fields = list(fields)
        self.title = title
        self.css_class = kwargs.pop('css_class', '')
        self.css_id = kwargs.pop('css_id', None)
        self.template = kwargs.pop('template', self.template)
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        fields = self.get_rendered_fields(form, form_style, context, template_pack, **kwargs)

        title = ''
        if self.title:
            title = '%s' % Template(text_type(self.title)).render(context)

        template = self.get_template_name(template_pack)
        return render_to_string(
            template,
            {'step': self, 'title': title, 'fields': fields, 'form_style': form_style}
        )


class Step(LayoutObject):
    """

    """
    template = "crispy-forms/layout/step.html"

    def __init__(self, title, *fields, **kwargs):
        self.fields = list(fields)
        self.title = title
        self.css_class = kwargs.pop('css_class', '')
        self.css_id = kwargs.pop('css_id', None)
        self.template = kwargs.pop('template', self.template)
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        fields = self.get_rendered_fields(form, form_style, context, template_pack, **kwargs)

        title = ''
        if self.title:
            title = '%s' % Template(text_type(self.title)).render(context)

        template = self.get_template_name(template_pack)
        return render_to_string(
            template,
            {'step': self, 'title': title, 'fields': fields, 'form_style': form_style}
        )

class StepFinal(LayoutObject):
    """

    """
    template = "crispy-forms/layout/step-final.html"

    def __init__(self, title, *fields, **kwargs):
        self.fields = list(fields)
        self.title = title
        self.css_class = kwargs.pop('css_class', '')
        self.css_id = kwargs.pop('css_id', None)
        self.template = kwargs.pop('template', self.template)
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        fields = self.get_rendered_fields(form, form_style, context, template_pack, **kwargs)

        title = ''
        if self.title:
            title = '%s' % Template(text_type(self.title)).render(context)

        template = self.get_template_name(template_pack)
        return render_to_string(
            template,
            {'step': self, 'title': title, 'fields': fields, 'form_style': form_style}
        )