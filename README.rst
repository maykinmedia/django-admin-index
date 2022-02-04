======================
Admin Index for Django
======================

:Version: 1.5.0
:Download: https://pypi.python.org/pypi/django_admin_index
:Source: https://github.com/maykinmedia/django-admin-index
:Keywords: django, admin, dashboard

|build-status| |coverage| |license| |pyversion| |djversion|

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

|screenshot-1| |screenshot-2| |screenshot-3|

Installation
============

You can install django_admin_index either via the Python Package Index (PyPI)
or from source.

To install using ``pip``:

.. code-block:: console

    $ pip install -U django_admin_index

Usage
=====

To use this with your project you need to follow these steps:

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

#. Create the database tables by performing a database migration:

   .. code-block:: console

      $ python manage.py migrate admin_index

#. Go to the Django admin of your site and look for the "Application groups"
   section.

Configuration
=============

There are 3 settings you can add to your ``settings.py``:

- ``ADMIN_INDEX_SHOW_REMAINING_APPS`` (defaults to ``False``)

  Show all models that are not added a to an `Application group` in a group
  called "Miscellaneous" for **staff** users.

  NOTE: If no `Application groups` are defined, it will show all models
  regardless of this setting.

- ``ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS`` (defaults to ``True``)

  Show all models that are not added a to an `Application group` in a group
  called "Miscellaneous" for **super users** users.

  NOTE: If no `Application groups` are defined, it will show all models
  regardless of this setting.

- ``ADMIN_INDEX_AUTO_CREATE_APP_GROUP`` (defaults to ``False``)

  Automaticly creates an `Application group`, based on the `app_label`, for
  all the models that would be in the "Miscellaneous" group. If ``True``, your
  Django admin will initially look as it normally would. It will not update
  existing `Application groups`.

- ``ADMIN_INDEX_SHOW_MENU`` (defaults to: ``True``)

  Show the admin index as a menu above the breadcrumbs. Submenu's are filled
  with the registered models.

* ``ADMIN_INDEX_HIDE_APP_INDEX_PAGES`` (defaults to: ``True``)

  Removes the links to the app index pages from the main index and the
  breadcrumbs.

* ``ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION`` (defaults to
  ``django_admin_index.utils.should_display_dropdown_menu``)

  A python dotted path that can be imported to check when the dropdown menu should be
  displayed in the admin. The default implementation displays this menu if the user is
  a staff user and ``ADMIN_INDEX_SHOW_MENU`` is enabled.

Extra
=====

Sticky header
-------------

The header (typically "Django administration") including the menu (added by this
library) and the breadcrumbs, all become sticky (ie. they stay visible when you scroll
down on large pages). If you don't want this, you can add some CSS lines, like::

    #header { position: initial; }
    .dropdown-menu { position: initial; }
    .breadcrumbs { position: initial; }


Breadcrumbs
-----------

You can also squeeze additional content in the breadcrumbs, just after
``Home``. Simply overwrite the block ``breadcrumbs_pre_changelist`` in the
admin templates you desire (``change_list.html``, ``change_form.html``, etc.)::

    {% block breadcrumbs_pre_changelist %}
    &rsaquo; Meaningful breadcrumb element
    {% endblock %}


.. |build-status| image:: https://secure.travis-ci.org/maykinmedia/django-admin-index.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/maykinmedia/django-admin-index

.. |coverage| image:: https://codecov.io/github/maykinmedia/django-admin-index/coverage.svg?branch=master
    :target: https://codecov.io/github/maykinmedia/django-admin-index?branch=master

.. |license| image:: https://img.shields.io/pypi/l/django-admin-index.svg
    :alt: BSD License
    :target: https://opensource.org/licenses/BSD-3-Clause

.. |pyversion| image:: https://img.shields.io/pypi/pyversions/django-admin-index.svg
    :alt: Supported Python versions
    :target: http://pypi.python.org/pypi/django-admin-index/

.. |djversion| image:: https://img.shields.io/badge/django-2.2%2C%203.0%2C%203.2%2C%204.0-blue.svg
    :alt: Supported Django versions
    :target: http://pypi.python.org/pypi/django-admin-index/


.. |screenshot-1| image:: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/dashboard_with_menu_thumb.png
    :alt: Ordered dashboard with dropdown menu.
    :target: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/dashboard_with_menu.png

.. |screenshot-2| image:: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/application_groups_thumb.png
    :alt: Manage Application groups.
    :target: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/application_groups.png

.. |screenshot-3| image:: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/change_user_management_group_thumb.png
    :alt: Configure application groups and add Application links.
    :target: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/change_user_management_group.png
