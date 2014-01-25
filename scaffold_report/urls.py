from django.conf.urls import *
from scaffold_report import views
from scaffold_report import report

report.autodiscover()

urlpatterns = patterns('',
    url('^(?P<name>\w+)/$', views.ScaffoldReportView.as_view(), name='scaffold-report'),
    url('^(?P<name>\w+)/view/$', views.DownloadReportView.as_view(), name='scaffold-report-download'),
    )
