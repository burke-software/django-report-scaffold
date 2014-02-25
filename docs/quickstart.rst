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

Setting up templates
--------------------
Next you want to customize your templates to make the reports feel at home. 
The default template to use is ``admin_base.html`` which could be a base template for your project.
You could also rename it.

Here is a example admin_base.html::

  {% extends 'base.html' %}
  {% load static %}
  
  {% block scripts %}
      {% include "scaffold_report/includes/header.html" %}
  {% endblock %}
  
  {% block content %}
  {% endblock %}
  
base.html is a base template for the Foo project. This can be anything you want. In my base.html I have
blocks called scripts and content. The content block is needed actually!

This method is easy but to customize further you could copy and change any of the scaffold report templates.
