==============
Change history
==============

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
