======================
Admin Index for Django
======================

:Version: 1.0.1
:Download: https://pypi.python.org/pypi/django_admin_index
:Source: https://github.com/maykinmedia/django-admin-index
:Keywords: django, admin, dashboard

|build-status| |coverage| |lintly| |license| |pyversion| |djversion|

About
=====

This extension enables you to group, order and customize the Django admin
index page without too much hassle or visual changes.

There are 2 concepts: `Application groups` and `Application links`. You can
create an application group and add any model to it in the Django admin, under
``Admin index``. Whether the models are shown to the user, depends on the
regular Django permissions and whether it's registered in the admin.

An application link is simply a URL with a name that you can add to an
application group. It shows as a regular Django model.

One final change in the Django admin is the removal of the App lists, that
link to a list of models within an App. This concept became obsolete.

Installation
============

You can install django_admin_index either via the Python Package Index (PyPI)
or from source.

To install using `pip`,:

.. code-block:: console

    $ pip install -U django_admin_index

Usage
=====

To use this with your project you need to follow these steps:

#. Install the django_admin_index library:

   .. code-block:: console

      $ pip install django_admin_index

#. Add ``django_admin_index`` and ``ordered_model`` to ``INSTALLED_APPS`` in
   your Django project's ``settings.py``. Make sure that
   ``django_admin_index`` comes before ``django.contrib.admin``::

    INSTALLED_APPS = (
        'django_admin_index',
        'ordered_model',
        ...,
        'django.contrib.admin',
    )

   Note that there is no dash in the module name, only underscores.

#. Add ``django_admin_index.context_processors.dashboard`` to the context
   processors in your Django project's ``settings.py``::

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'django_admin_index.context_processors.dashboard'
                ],
            },
        },
    ]

#. Create the database tables by performing a database migration:

   .. code-block:: console

      $ python manage.py migrate admin_index

#. Go to the Django admin of your site and look for the "Application groups"
   section.

Configuration
=============

There are 2 settings you can add to your ``settings.py``:

- ``ADMIN_INDEX_SHOW_REMAINING_APPS`` (defaults to ``False``)

  Show all models that are not added a to an `Application group` in a group
  called "Miscellaneous" for **staff** users.

- ``ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS`` (defaults to ``True``)

  Show all models that are not added a to an `Application group` in a group
  called "Miscellaneous" for **super users** users.

- ``ADMIN_INDEX_AUTO_CREATE_APP_GROUP`` (defaults to ``False``)

  Automaticly creates an `Application group`, based on the `app_label`, for
  all the models that would be in the "Miscellaneous" group. If ``True``, your
  Django admin will initially look as it normally would.


.. |build-status| image:: https://secure.travis-ci.org/maykinmedia/django-admin-index.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/maykinmedia/django-admin-index

.. |coverage| image:: https://codecov.io/github/maykinmedia/django-admin-index/coverage.svg?branch=master
    :target: https://codecov.io/github/maykinmedia/django-admin-index?branch=master

.. |lintly| image:: https://lintly.com/gh/maykinmedia/django-admin-index/badge.svg
    :target: https://lintly.com/gh/maykinmedia/django-admin-index/
    :alt: Lintly

.. |license| image:: https://img.shields.io/pypi/l/django-admin-index.svg
    :alt: BSD License
    :target: https://opensource.org/licenses/BSD-3-Clause

.. |pyversion| image:: https://img.shields.io/pypi/pyversions/django-admin-index.svg
    :alt: Supported Python versions
    :target: http://pypi.python.org/pypi/django-admin-index/

.. |djversion| image:: https://img.shields.io/badge/django-1.8%2C%201.9%2C%201.10%2C%201.11%2C%202.0-blue.svg
    :alt: Supported Django versions
    :target: http://pypi.python.org/pypi/django-admin-index/
