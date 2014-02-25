Quickstart Guide
================

Installation
------------
1. ``pip install django-report-scaffold``
2. Add ``scaffold_report`` to ``INSTALLED_APPS``
3. Add ``(r'^reports/', include('scaffold_report.urls')),`` to ``urls.py``. I choose to name it "reports" but make it whatever you want.
4. It's installed but won't do anything yet!

Creating your first report
--------------------------
Create a file called ``scaffold_reports.py`` in your projects app folder. Here is a sample report to get started.::

  from foo.models import Order
  from scaffold_report.report import ScaffoldReport, scaffold_reports
  
  class FooReport(ScaffoldReport):
      name = "Reports"
      model = Order
      filters = (
      )
  
  scaffold_reports.register('foo_report', FooReport)

Now go to ``/reports/foo_report/`` to view it in a browser.
