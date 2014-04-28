"""
.. module:: filters
   :platform: Unix, Windows
   :synopsis: A useful module indeed.

.. moduleauthor::
"""

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.http import QueryDict
from .fields import SimpleCompareField
from abc import abstractmethod
import inspect
import six
import re

class Filter(object):
    """ A customized filter for querysets """
    #: Unique name of filter
    name = None
    #: Human readable name of filter
    verbose_name = None
    #: If set the filter will render using this django template
    #: If not set the filter will render using scaffold_report/filter.html
    template_name = None
    #: Define fields here that will be appended together to make a generic form
    fields = None
    #: Optional form class to use.
    form_class = None
    #: Optional form. If not set, an instance of the form_class will be used
    form = None
    #: uncleaned_form data from the post
    raw_form_data = None
    #: Add these fields to the preview and spreadsheet reports
    add_fields = []
    #: Show this filter as on by default
    default = False
    #: User is able to delete this filter. Should be used with default = True.
    can_remove = True
    #: User is able to add this filter
    can_add = True

    def __init__(self, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)
        self.build_form()

    @abstractmethod
    def queryset_filter(self, queryset, report_context=None, form=None):
        """ Allow custom handeling of queryset
        Must return the queryset.
        """
        return queryset

    def render_form(self):
        """ Render the form using a template
        Only called if template_name is defined """
        context = self.get_template_context()
        return render_to_string(self.template_name, context)

    def get_add_fields(self):
        """ Returns the fields to add to previews and spreadsheet reports """
        return self.add_fields

    def process_filter(self, queryset, report_context=None):
        """ Run the actual filter based on client data """
        is_valid = self.get_form_data()
        if is_valid:
            return self.queryset_filter(queryset, report_context=report_context)
        else:
            return queryset

    def get_template_context(self):
        """ Get the context to be shown when rendering a template just
        for this filter """
        context = {}
        if self.form:
            context['form'] = self.form
        return context

    def get_report_context(self, report_context):
        """ Process any data that needs set for an entire report """
        return report_context

    def build_form(self):
        """ Construct form out of fields or form """
        if not self.form_class:
            self.form_class = forms.Form
        self.form = self.form_class()

        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())
        if self.fields:
            for i, field in enumerate(self.fields):
                if inspect.isclass(field):
                    self.form.fields['field_' + str(i)] = field()
                else:
                    self.form.fields['field_' + str(i)] = field
                self.form.fields['field_' + str(i)].label = ''

    def get_form_data(self):
        form_dict = QueryDict(self.raw_form_data)
        # Manually bound the form instead of Form(data)
        self.form.data = form_dict
        self.form.is_bound = form_dict
        if self.form.is_valid():
            self.cleaned_data = self.form.cleaned_data
            return True
        else:
            return False

    def get_verbose_name(self):
        if self.verbose_name:
            return self.verbose_name
        name = self.get_name()
        return re.sub(r"(\w)([A-Z])", r"\1 \2", name)

    def get_name(self):
        """ return unique name of this filter """
        if self.name:
            return self.name
        return self.__class__.__name__


class DecimalCompareFilter(Filter):
    """ X greater, less, etc than decimal field """
    fields = [
        SimpleCompareField,
        forms.DecimalField(decimal_places=2, max_digits=6, min_value=0,),
    ]
    compare_field_string = None

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        compare = self.cleaned_data['field_0']
        value = self.cleaned_data['field_1']
        compare_kwarg = {self.compare_field_string + '__' + compare: value}
        return queryset.filter(**compare_kwarg)


class ModelChoiceFilter(Filter):
    """ Select object from a queryset """
    fields = [forms.ModelChoiceField,]
    #: String used in the Django orm filter function. See queryset_filter()
    compare_field_string = None
    #: Model used for queryset. Set this for any object of such model.
    model = None
    #: queryset that populates the widget. Model is not needed if this is set.
    queryset = None

    def get_queryset(self):
        """ Get the queryset that will populare the widget """
        if self.queryset:
            return self.queryset
        return self.model.objects.all()

    def build_form(self):
        queryset = self.get_queryset()
        self.form = forms.Form()
        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())
        self.form.fields['field_0'] = forms.ModelChoiceField(queryset, label='')

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        selected = self.cleaned_data['field_0']
        compare_kwarg = {self.compare_field_string: selected}
        return queryset.filter(**compare_kwarg)


class ModelMultipleChoiceFilter(ModelChoiceFilter):
    """ Select multiple objects from a queryset """
    fields = [forms.ModelMultipleChoiceField,]

    def build_form(self):
        queryset = self.get_queryset()
        self.form = forms.Form()
        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())
        self.form.fields['field_0'] = forms.ModelMultipleChoiceField(queryset, label='')

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        selected = self.cleaned_data['field_0']
        compare_kwarg = {self.compare_field_string + '__in': selected}
        return queryset.filter(**compare_kwarg)


class IntCompareFilter(DecimalCompareFilter):
    """ x greater, less, etc than int field """
    fields = [
        SimpleCompareField,
        forms.IntegerField(),
    ]

