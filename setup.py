from setuptools import setup, find_packages

setup(
    name = "django-report-scaffold",
    version = "0.1.4",
    author = "David Burke",
    author_email = "david@burkesoftware.com",
    description = ("Create streamlined and flexible reporting tools for your end uesrs. Report scaffold is not a drop in application but a framework for creating reporting tools. Think of it like django admin."),
    license = "BSD",
    keywords = "django report",
    url = "https://github.com/burke-software/django-report-scaffold",
    packages=find_packages(),
    include_package_data=True,
    test_suite='setuptest.setuptest.SetupTestSuite',
    tests_require=(
        'django-setuptest',
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        'django',
        'django-report-utils',
        'django-widget-tweaks',
    ]
)
