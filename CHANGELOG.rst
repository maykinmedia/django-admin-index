==============
Change history
==============

2.0.1 (2022-06-16)
==================

Bugfix release for the calendar/timebox modals.

* Fixed z-index for calendar popup
* Fixed z-index for timebox popup

2.0.0
=====

*March 15, 2022*

This release contains breaking changes in the admin markup and stylesheets, hence the
major version bump.

Breaking changes
----------------

* Dropped support for non-LTS Django versions (1.11, 3.0). Only Django 2.2, 3.2 and 4.0
  are officially supported and tested.
* Fixed #69 -- Properly namespaced the ``includes/app_list.html`` template to
  ``django_admin_index/includes/app_list.html``
* Refactored the styling (#71)

    * All django-admin-index classnames now have a ``djai-`` prefix to prevent
      collissions (e.g. bootstrap has a ``dropdown-menu`` as well)
    * Colour definitions now leverage the Django 3.2 CSS variables, see
      ``scss/_vars.scss``. For Django < 3.2 these don't exist, but the fallback values
      are defined. This makes it easier to theme django-admin-index in your project by
      just overriding the CSS variables instead of the entire relevant selector.
    * The markup of the ``django_admin_index/includes/app_list.html`` has been slightly
      modified, some class names are moved around.
    * The breadcrumbs are no longer sticky/fixed by default, override this in your own
      styling if desired. Possibly in the future this may be controllable with a CSS var.
    * Made a mimimal working layout on mobile. Tabs wrap on the next line and the menus
      are no longer hidden behind the breadcrumbs.

* Reduced amount of overridden ``django.contrib.admin`` template code - people
  overriding the django-admin-index templates may want to revisit these.

Other improvements
------------------

* Added optional support for Django Debug Toolbar
* Added template overrides for ``registration/password_reset_form.html`` and
  ``registration/password_reset_done.html``
* Updated isort config to be black-compatible
* Updated test project (used for local testing and CI) to Django 2.2 and Django 3.2+
* Included ``AppConfig.default_auto_field`` for Django 3.2+
* Fixed stylesheet being loaded in the body instead of the head (#70)
* Restructured packaging setup and repository layout (#73)

1.6.0
=====

*February 14, 2022*

* Added support for Django 3.0, 3.2 and 4.0, on supported Python versions (#47)
* Removed merge conflicts from CSS-file (#46)
* Moved to Github actions (#61)

1.5.0
=====

* Updated package metadata
* Added setting ``ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION`` to provide
  more control on when to display/hide the dropdown menu. The default implementation
  is backwards compatible.

1.4.0
=====

* Fixed #31 -- Prevent excessive queries by changing the context processor to 
  template tags (thanks @svenvandescheur).
* Fixes #41 -- Added missing migration.
* Fixed #34 -- Don't show item if the menu item URL is undefined.
* Fixed #33 -- Don't show a warning if the Django Admin AppConfig is overriden.
* Fixed #29 -- Added screenshots to README.

1.3.1
=====

*July 21, 2020*

* Added active dashboard link tests for different perms.
* Added shadow to dropdown.
* Fixed active menu item for groups without change/read permission.
* Updated npm package requirements (only needed for development).

1.3.0
=====

*January 20, 2020*

* Removed Django 1.11 support.
* Removed Python 2.7 support.
* Added Django 3.0 support.
* Added support for Python 3.8 (for eligable Django versions).
* Updated Travis CI config to test all supported Python and Django versions.
* Now depends on ``django-ordered-model`` version 3.0 (or higher)

1.2.3
=====

*January 16, 2020*

* Fixed incorrect menu positioning (white line showing).

1.2.2
=====

*December 5, 2019*

* Removed accidental print statement.
* Added undocumented change in 1.2.1 changelog regarding the template block
  ``breadcrumbs_pre_changelist``.

1.2.1
=====

*November 29, 2019*

* Added ``ADMIN_INDEX_SHOW_MENU`` setting to show (default) or hide the extra
  menu.
* Added ``ADMIN_INDEX_HIDE_APP_INDEX_PAGES`` setting to show or hide (default)
  the application index page link in the breadcrumbs and on the main index
  page.
* Added template block ``breadcrumbs_pre_changelist`` which can be overriden
  to add a custom breadcrumb between home and the list view.

1.2.0
=====

*October 18, 2019*

* Fixed ``AUTO_CREATE_APP_GROUP`` setting to show auto generated groups on the
  very first time you render the admin.
* Fixed an issue where staff users didn't see anything if no ``AppGroups`` were
  created and showing remaining apps was turned off (thanks @sergeimaertens).
* Fixed admin templates to work with the view permission introduced in
  Django 2.1.
* Updated npm package requirements (only needed for development).


1.1.0
=====

*October 14, 2019*

* Added navigation menu based on ``AppGroup`` configuration (thanks @JostCrow).
* Removed Django < 1.11 support.
* Updated test requirements.


1.0.1
=====

*March 12, 2018*

* Fixed a bug with the ``AppGroup`` creation that occurs when the same slug
  with and a different ``app_name`` would be created.
* Using the AppConfig verbose name instead of the model name.


1.0
===

*December 18, 2017*

* Added Django 2.0 support.


0.9.1
=====

*November 3, 2017*

* Added natural keys for all models.
* Added ``ADMIN_INDEX_AUTO_CREATE_APP_GROUP`` setting to create groups
  automatically, if the model was not yet in a group.


0.9.0
=====

*July 3, 2017*

* Initial public release on PyPI.
