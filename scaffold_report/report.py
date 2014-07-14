from django.conf import settings
import copy

class ScaffoldReport(object):
    """ Base class for any actual scaffold reports
    A scaffold report is named after UI effects for moving
    various filters and previews into the report
    building screen. All reports require customized
    options set by the programmer.
    """
    #: Unique name of report.
    name = ""
    #: Verbose name of report to show users.
    name_verbose = None
    #: Base model for this report's queryset.
    model = None
    #: Array of field names to show on previews.
    preview_fields = ['id']
    #: How many objects in the queryset should be show in preview.
    num_preview = 3
    #: Filters that can be applied to the report.
    filters = []
    #: Buttons will show in sidebar area. These can be premade reports and give the
    #: user more options than just clicking submit
    report_buttons = []
    #: Report is only viewable to those with these permissions.
    #: Will default to the model's change permission if not set
    permissions_required = []
    #: A statically defined template. Could override get_template instead.
    appy_template = None

    def __init__(self):
        self._possible_filters = [] # developer selected filters from subclass
        self._active_filters = [] # end user selected filters from view
        self.report_context = {}
        self.filter_errors = []
        self.add_fields = []
        field_names = []
        for possible_filter in self.filters:
            if possible_filter.get_name() in field_names:
                raise Exception(
                    'Duplicate field names in scaffold report. '\
                    'Please set a different name for {}.'.format(possible_filter.get_name()))
            field_names += [possible_filter.get_name()]
            self._possible_filters += [possible_filter]

    def get_appy_template(self):
        """ Return a appy template
        This could be hard coded or perhaps get report_context from a filter.
        """
        if self.appy_template:
            return self.appy_template

    def check_permissions(self, request):
        """ Return true is user has permission to view page """
        if self.permissions_required:
            return request.user.has_perms(self.permissions_required)
        else:
            return request.user.has_perm(
                    '{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    @property
    def get_name(self):
        """ Return name_verbose if it has been set; otherwise
        return name. Replaces all spaces with underscores. """
        if self.name_verbose != None:
            return self.name_verbose
        return self.name.replace('_', ' ')

    def handle_post_data(self, data):
        for filter_data in data:
            for possible_filter in self._possible_filters:
                if possible_filter.__class__.__name__ == filter_data['name']:
                    filter_instance = copy.copy(possible_filter)
                    filter_instance.build_form()
                    filter_instance.raw_form_data = filter_data.get('form', None)
                    self._active_filters += [filter_instance]
                    if not filter_instance.get_form_data():
                        self.filter_errors += [{
                            'filter': filter_instance.form.data['filter_number'],
                            'errors': filter_instance.form.errors,
                        }]

    def get_queryset(self):
        """ Return a queryset of the model
        filtering any active filters
        """
        report_context = {}
        queryset = self.model.objects.all()
        for active_filter in self._active_filters:
            queryset = active_filter.process_filter(queryset, self.report_context)
            if active_filter.form.errors:
                pass
            else:
                report_context = active_filter.get_report_context(report_context)
                self.add_fields += active_filter.get_add_fields()
            self.report_context = dict(self.report_context.items() + report_context.items())
        return queryset

    def get_appy_context(self):
        """ Return a context dict for use in an appy template
        Acts a like context in Django template rendering.
        """
        appy_context = {}
        appy_context['objects'] = self.get_queryset()
        return appy_context

    def report_to_list(self, user, preview=False):
        """ Convert to python list """
        queryset = self.get_queryset()
        if preview and False:
            queryset = queryset[:self.num_preview]

        if self.preview_fields:
            preview_fields = self.preview_fields
        else:
            preview_fields = ['__unicode__']

        result_list = []
        for obj in queryset:
            result_row = []
            for field in preview_fields:
                field = self.get_field_name(field)
                cell = getattr(obj, field)
                if callable(cell):
                    cell = cell()
                result_row += [cell]
            for field in self.add_fields:
                cell = getattr(obj, field)
                if callable(cell):
                    cell = cell()
                result_row += [cell]

            result_list += [result_row]
        return result_list

    def get_field_verbose(self, field):
        if isinstance(field, tuple) and len(field) == 2:
            field = field[1]
        return field

    def get_field_name(self, field):
        if isinstance(field, tuple) and len(field) == 2:
            field = field[0]
        return field


    def get_preview_fields(self):
        if self.preview_fields:
            preview_fields = []
            all_preview_fields = self.preview_fields + self.add_fields
            for field in all_preview_fields:
                field = self.get_field_verbose(field)
                try:
                    preview_fields += [self.model._meta.get_field_by_name(field)[0].verbose_name.title()]
                except:
                    preview_fields += [field.replace('_', ' ')]
            return preview_fields
        else:
            return [self.model._meta.verbose_name_plural.title()]


class ReportButton(object):
    """ An alternative way to submit a report.
    Could be used for one off reports that behave differently.
    """
    #: For button name attr
    name = ""
    name_verbose = None
    #: For button value attr
    value = ""
    #: When true the queryset is processed first (so filters will run) and passed to get_report
    accepts_queryset = True

    @property
    def get_name(self):
        """ Return name_verbose if it has been set; otherwise
        return name. Replaces all spaces with underscores. """
        if self.name_verbose != None:
            return self.name_verbose
        return self.name.replace('_', ' ')

    def get_report(self, context=None):
        """ This function will call to generate the actual report
        Should return a valid response """
        pass


try:
    from collections import OrderedDict
except:
    OrderedDict = dict # pyflakes:ignore

def autodiscover():
    """
    Auto-discover INSTALLED_APPS report.py modules and fail silently when
    not present. Borrowed form django.contrib.admin
    """
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    global scaffold_reports

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try:
            before_import_registry = copy.copy(scaffold_reports)
            import_module('%s.scaffold_reports' % app)
        except:
            scaffold_eports = before_import_registry
            if module_has_submodule(mod, 'scaffold_reports'):
                raise

class ScaffoldReportClassManager(object):
    """
    Class to handle registered reports class.
    Borrowed from django-model-report Thanks!
    """
    _register = OrderedDict()

    def __init__(self):
        self._register = OrderedDict()

    def register(self, slug, rclass):
        if slug in self._register:
            raise ValueError('Slug already exists: %s' % slug)
        setattr(rclass, 'slug', slug)
        self._register[slug] = rclass

    def get_report(self, slug):
        # return class
        return self._register.get(slug, None)

    def get_reports(self):
        # return clasess
        return self._register.values()


scaffold_reports = ScaffoldReportClassManager()
