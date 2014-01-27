###################################################
The edX Learning Management System (LMS)
###################################################

The edX Learning Management System (LMS) is a Django application.

The root of the LMS is in the edX platform/lms directory.

Configuration settings for the LMS are in the lms/envs directory.


***********************************
The Django Auth System
***********************************

The LMS uses use the Django Auth system, including the is\_staff and is\_superuser flags. User profiles and related code is in the ``lms/djangoapps/student/`` directory. There is support for groups of students (for example, for those who want email about future courses) in ``lms/djangoapps/student/models.py``.

***********************************
The Student Module
***********************************

The student module keeps track of where a particular student is in a module, their grade, and when they started and completed the module.  The student module uses ``lms/djangoapps/courseware/models.py``.

-  Core rendering path:
-  ``lms/urls.py`` points to ``courseware.views.index``, which gets
   module info from the course xml file, pulls list of ``StudentModule``
   objects for this user (to avoid multiple db hits).

-  Calls ``render_accordion`` to render the "accordion"--the display of
   the course structure.

-  To render the current module, calls
   ``module_render.py:render_x_module()``, which gets the
   ``StudentModule`` instance, and passes the ``StudentModule`` state
   and other system context to the module constructor the get an
   instance of the appropriate module class for this user.

-  calls the module's ``.get_html()`` method. If the module has nested
   submodules, render\_x\_module() will be called again for each.

-  ajax calls go to ``module_render.py:handle_xblock_callback()``, which
   passes it to one of the ``XBlock``\ s handler functions

-  See ``lms/urls.py`` for the wirings of urls to views.

-  Tracking: there is support for basic tracking of client-side events
   in ``lms/djangoapps/track``.

