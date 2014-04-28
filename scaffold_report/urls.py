from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from scaffold_report import views
from scaffold_report import report

report.autodiscover()

urlpatterns = patterns('',
    url('^(?P<name>\w+)/$', login_required(views.ScaffoldReportView.as_view()), name='scaffold-report'),
    url('^(?P<name>\w+)/view/$', login_required(views.DownloadReportView.as_view()), name='scaffold-report-download'),
    )
