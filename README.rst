======================
Admin Index for Django
======================

:Version: 2.0.2
:Download: https://pypi.python.org/pypi/django-admin-index
:Source: https://github.com/maykinmedia/django-admin-index
:Keywords: django, admin, dashboard

|build-status| |code-quality| |black| |coverage| |license| |python-versions| |django-versions| |pypi-version|

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

    $ pip install -U django-admin-index

Usage
=====

To use this with your project you need to follow these steps:

#. Add ``django_admin_index`` and ``ordered_model`` to ``INSTALLED_APPS`` in
   your Django project's ``settings.py``. Make sure that
   ``django_admin_index`` comes before ``django.contrib.admin``:

   .. code-block:: python

      INSTALLED_APPS = (
          "django_admin_index",
          "ordered_model",
          ...,
          "django.contrib.admin",
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

Theming
-------

By default, django-admin-index tabs/dropdowns are styled in the Django admin theme
colours. On Django 3.2+ these are controlled through CSS variables in the
``static/admin/css/base.css`` stylesheet. These CSS variables are used as defaults for
django-admin-index' own CSS variables.

See ``scss/_vars.scss`` for all the available CSS variables you can use to customize
the color palette. A simple example:

.. code-block:: css

    :root {
      --djai-tab-bg: #ff0080;
      --djai-tab-bg--hover: #a91b60;
    }

Any rules not supported by CSS vars can be overridden with regular CSS. All elements
have CSS class names following the BEM methodology, such as
``.djai-dropdown-menu__item`` and
``.djai-dropdown-menu__item.djai-dropdown-menu__item--active``.


Sticky header
-------------

The header (typically "Django administration") including the menu (added by this
library) become sticky (ie. they stay visible when you scroll down on large pages). If
you don't want this, you can add some CSS lines, like:

.. code-block:: css

    #header { position: initial; }
    .djai-dropdown-menu { position: initial; }


Breadcrumbs
-----------

You can also squeeze additional content in the breadcrumbs, just after
``Home``. Simply overwrite the block ``breadcrumbs_pre_changelist`` in the
admin templates you desire (``change_list.html``, ``change_form.html``, etc.)

.. code-block:: django

    {% block breadcrumbs_pre_changelist %}
    &rsaquo; Meaningful breadcrumb element
    {% endblock %}


Contributors
============

Contributors and maintainers can install the project locally with all test dependencies
in a virtualenv:

.. code-block:: bash

    (env) $ pip install -e .[tests,pep8,coverage,release]

Running the test suite
----------------------

To run the tests for a single environment (currently installed in your virtualenv), use
``pytest``:

.. code-block:: bash

    (env) $ pytest

To run the complete build matrix, use ``tox``:

.. code-block:: bash

    (env) $ tox

Developing the frontend
-----------------------

To develop the stylesheets, you can use the included test project:

.. code-block:: bash

    (env) $ python manage.py runserver

You also want to install the frontend tooling and run the SCSS compilation to CSS in
watch mode:

.. code-block:: bash

    npm install  # one time to get the dependencies installed
    npm run watch

Once the result is satisfactory, you can make a production build of the stylesheets:

.. code-block:: bash

    npm run scss

Then, commit the changes and make a pull request.


.. |build-status| image:: https://github.com/maykinmedia/django-admin-index/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/django-admin-index/actions/workflows/ci.yml

.. |code-quality| image:: https://github.com/maykinmedia/django-admin-index/workflows/Code%20quality%20checks/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/django-admin-index/actions?query=workflow%3A%22Code+quality+checks%22

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |coverage| image:: https://codecov.io/github/maykinmedia/django-admin-index/coverage.svg?branch=master
    :target: https://codecov.io/github/maykinmedia/django-admin-index?branch=master

.. |license| image:: https://img.shields.io/pypi/l/django-admin-index.svg
    :alt: BSD License
    :target: https://opensource.org/licenses/BSD-3-Clause

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/django-admin-index.svg
    :alt: Supported Python versions
    :target: http://pypi.python.org/pypi/django-admin-index/

.. |django-versions| image:: https://img.shields.io/badge/django-2.2%2C%203.0%2C%203.2%2C%204.0-blue.svg
    :alt: Supported Django versions
    :target: http://pypi.python.org/pypi/django-admin-index/

.. |pypi-version| image:: https://img.shields.io/pypi/v/django-admin-index.svg
    :target: https://pypi.org/project/django-admin-index/

.. |screenshot-1| image:: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/dashboard_with_menu_thumb.png
    :alt: Ordered dashboard with dropdown menu.
    :target: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/dashboard_with_menu.png

.. |screenshot-2| image:: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/application_groups_thumb.png
    :alt: Manage Application groups.
    :target: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/application_groups.png

.. |screenshot-3| image:: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/change_user_management_group_thumb.png
    :alt: Configure application groups and add Application links.
    :target: https://github.com/maykinmedia/django-admin-index/raw/master/docs/_assets/change_user_management_group.png
