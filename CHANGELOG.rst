==============
Change history
==============

1.1.0
=====

*October 14, 2019*

* Added navigation menu based on ``AppGroup`` configuration.
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
