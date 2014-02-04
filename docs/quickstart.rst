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
Create a file called ``scaffold_reports.py`` in your projects app folder.


