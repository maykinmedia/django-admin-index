======================
Admin Index for Django
======================

:Version: 0.9.0
:Download: https://pypi.python.org/pypi/django_admin_index
:Source: https://github.com/maykinmedia/django-admin-index
:Keywords: django, admin, dashboard

|build-status| |coverage|

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

#. Install the django_celery_monitor library:

   .. code-block:: console

      $ pip install django_admin_index

#. Add ``django_admin_index`` to ``INSTALLED_APPS`` in your
   Django project's ``settings.py``, before ``django.contrib.admin``::

    INSTALLED_APPS = (
        'django_admin_index',
        ...,
        'django.contrib.admin',
    )

   Note that there is no dash in the module name, only underscores.

#. Create the database tables by performing a database migrations:

   .. code-block:: console

      $ python manage.py migrate django_admin_index

#. Go to the Django admin of your site and look for the "Admin Index"
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


.. |build-status| image:: https://secure.travis-ci.org/maykinmedia/django-admin-index.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/maykinmedia/django-admin-index

.. |coverage| image:: https://codecov.io/github/maykinmedia/django-admin-index/coverage.svg?branch=master
    :target: https://codecov.io/github/maykinmedia/django-admin-index?branch=master
