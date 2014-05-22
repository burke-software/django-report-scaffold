from django.core.servers.basehttp import FileWrapper
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import ProcessFormView
import simplejson
from report_utils.utils import DataExportMixin
from .report import scaffold_reports
import tempfile
import json
import time
import os

class ScaffoldReportMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.report = scaffold_reports.get_report(kwargs['name'])()
        except KeyError:
            raise Http404
        if self.report.check_permissions(request) == False:
            return HttpResponseForbidden()
        self.model = self.report.model
        return super(ScaffoldReportMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ScaffoldReportMixin, self).get_context_data(**kwargs)
        context['report'] = self.report
        context['filters'] = self.report.filters
        return context


class ScaffoldReportView(ScaffoldReportMixin, TemplateView):
    """ Base class for reporting """
    template_name = "scaffold_report/report.html"


class DownloadReportView(DataExportMixin, ScaffoldReportMixin, TemplateView):
    """ Show the report in various ways """
    template_name = "scaffold_report/table.html"

    def post(self, request, **kwargs):
        download_type = request.GET.get('type')
        context = self.get_context_data(**kwargs)
        if request.POST.get('data', None):
            data = simplejson.loads(request.POST['data'])
            self.report.handle_post_data(data)
            if download_type == "preview":
                preview=True
            else:
                preview=False
            context['object_list'] = self.report.report_to_list(
                user=self.request.user, preview=preview)
            context['headers'] = self.report.get_preview_fields()

        for button in self.report.report_buttons:
            if button.name == download_type:
                return button.get_report(self, context)

        if download_type == "preview":
            preview_html = render_to_string(self.template_name, context)
            response_data = {}
            response_data['preview_html'] = preview_html
            response_data['filter_errors'] = self.report.filter_errors
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        elif download_type == "xlsx":
            data = self.report = context['object_list']
            return self.list_to_xlsx_response(data)
        elif download_type == 'django_admin':
            ids = self.report.get_queryset().values_list('id', flat=True)
            ids = ",".join(str(x) for x in ids)
            response = redirect('admin:{}_{}_changelist'.format(
                self.model._meta.app_label, self.model._meta.model_name))
            response['Location'] += '?id__in={}'.format(ids)
            return response
        elif download_type == "appy":
            filename = 'report'
            ext = '.odt'
            appy_context = self.report.get_appy_context()
            template_name = self.report.get_appy_template()
            from appy.pod.renderer import Renderer
            outfile_name = tempfile.gettempdir() + '/appy' + str(time.time()) + ext
            renderer = Renderer(template_name, appy_context, outfile_name)
            renderer.run()

            if ext == ".doc":
                content = "application/msword"
            elif ext == ".docx":
                content = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == ".pdf":
                content = "application/pdf"
            elif ext == ".rtf":
                content = "application/rtf"
            elif ext == '.ods':
                content = "application/vnd.oasis.opendocument.spreadsheet"
            else: # odt
                content = "application/vnd.oasis.opendocument.text"

            wrapper = FileWrapper(file(outfile_name))
            response = HttpResponse(wrapper, content_type=content)
            response['Content-Length'] = os.path.getsize(outfile_name)
            response['Content-Disposition'] = 'attachment; filename=' + filename + ext
            try: os.remove(file_name)
            except: pass # At least it's in the tmp folder
            return response

