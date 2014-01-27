###################################################
Documentation for the edX Platform
###################################################

This chapter introduces the edX platform:

*
*
*

**************************
Open edX
**************************

EdX code is open source. You can explore our main project, `edx-platform <https://github.com/edx/edx-platform>`_, as well as all of our `other projects <https://github.com/edx>`_, on GitHub. 

**************************
Communication Channels
**************************

You can interact with the open source community through the mailing list edx-code@googlegroups.com.

You can also use the #edx-code IRC channel.


****************************
Software Development Skills
****************************

Most of edX code is Python 2.7 (not Python 3.)  In addition to Python, to work with the edX platform you should be familiar with:

* Django
* Mako templates
* JavaScript
* HTML, XML, XPath, XSLT
* CSS
* Git


****************************
System Overview
****************************

The following list describes the major components of the edX system.


* **Learning Management System (LMS)**: The LMS contains the student-facing parts of the edX platform.  The LMS handles student accounts, displaying course content and videos videos, showing problems and exams, and other course elements. 

* **Course Management System (CMS)**: The CMS is the system course staff use to build courses. The CMS allows multiple instructors to add course content, set grading policies, create problems, and provide other course information.

* **Discussion Forums**: Discussion forums use a Ruby on Rails service that runs on Heroku. Discussion forums are embedded in the LMS.

* **Course Data**: Course data is stored in the data directory. The file course.xml, along with XML files in sub-directories, stores the course content

.. note:: **CAPA**: `lon-capa.org <lon-capa.org>`_ is the content management system that has defined a
   standard for online learning and assessment materials. Much of the edX platform follows this standard.


****************************
Common Libraries
****************************

The following list describes the common libraries in the edX platform.

* **xmodule**: xmodules are generic learning modules. *x* can be sequence, video,
   template, html, vertical, capa, etc. These are the objects that one
   puts inside sections in the course structure.

   -  XModuleDescriptor: This defines the problem and all data and UI
      needed to edit that problem. It is unaware of any student data,
      but can be used to retrieve an XModule, which is aware of the
      student's state.

   -  XModule: The XModule is a problem instance that is particular to a
      student. The XModule renders the problem as html, scores itself, and handles AJAX calls from
      the browser.

   -  Both XModule and XModuleDescriptor take system context parameters.
      These are named ModuleSystem and DescriptorSystem respectively.
      These help isolate the XModules from any interactions with
      external resources that they require.

      For instance, the DescriptorSystem has a function to load an
      XModuleDescriptor from a Location object, and the ModuleSystem
      knows how to render objects, track events, and generate 404 errors.

   -  XModules and XModuleDescriptors are uniquely identified by a
      Location object, encoding the organization, course, category,
      name, and possibly revision of the module.

   -  XModule initialization: XModules are instantiated by the
      ``XModuleDescriptor.xmodule`` method, and given a ModuleSystem,
      the descriptor which instantiated it, and their relevant model
      data.

   -  XModuleDescriptor initialization: If an XModuleDescriptor is
      loaded from an XML-based course, the XML data is passed into its
      ``from_xml`` method, which is responsible for instantiating a
      descriptor with the correct attributes. If it's in Mongo, the
      descriptor is instantiated directly. The module's attributes will
      be present in the ``model_data`` dict.

   -  ``course.xml`` format. We use python setuptools to connect
      supported tags with the descriptors that handle them. See
      ``common/lib/xmodule/setup.py``. There are checking and validation
      tools in ``common/validate``.

      -  the xml import+export functionality is in
         ``xml_module.py:XmlDescriptor``, which is a mixin class that's
         used by the actual descriptor classes.

      -  There is a distinction between descriptor *definitions* that
         stay the same for any use of that descriptor (e.g. here is what
         a particular problem is), and *metadata* describing how that
         descriptor is used (e.g. whether to allow checking of answers,
         due date, etc). When reading in ``from_xml``, the code pulls
         out the metadata attributes into a separate structure, and puts
         it back on export.

   -  Xmodule code is located in ``common/lib/xmodule``

-  **capa**: Capa modules define LoncapaProblem and many related things.

   -  Capa code is located in ``common/lib/capa``






LMS
~~~

The LMS is a django site, with root in ``lms/``. It runs in many
different environments--the settings files are in ``lms/envs``.

-  We use the Django Auth system, including the is\_staff and
   is\_superuser flags. User profiles and related code lives in
   ``lms/djangoapps/student/``. There is support for groups of students
   (e.g. 'want emails about future courses', 'have unenrolled', etc) in
   ``lms/djangoapps/student/models.py``.

-  ``StudentModule`` -- keeps track of where a particular student is in
   a module (problem, video, html)--what's their grade, have they
   started, are they done, etc. [This is only partly implemented so
   far.]

   -  ``lms/djangoapps/courseware/models.py``

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

CMS
~~~

The CMS is a django site, with root in ``cms``. It can run in a number
of different environments, defined in ``cms/envs``.

-  Core rendering path: Still TBD

Static file processing
~~~~~~~~~~~~~~~~~~~~~~

-  CSS -- we use a superset of CSS called SASS. It supports nice things
   like includes and variables, and compiles to CSS. The compiler is
   called ``sass``.

-  javascript -- we use coffeescript, which compiles to js, and is much
   nicer to work with. Look for ``*.coffee`` files. We use *jasmine* for
   testing js.

-  *mako* -- we use this for templates, and have wrapper called edxmako
   that makes mako look like the django templating calls.

We use a fork of django-pipeline to make sure that the js and css always
reflect the latest ``*.coffee`` and ``*.sass`` files (We're hoping to
get our changes merged in the official version soon). This works
differently in development and production. Test uses the production
settings.

In production, the django ``collectstatic`` command recompiles
everything and puts all the generated static files in a static/ dir. A
starting point in the code is
``django-pipeline/pipeline/packager.py:pack``.

In development, we don't use collectstatic, instead accessing the files
in place. The auto-compilation is run via
``common/djangoapps/pipeline_mako/templates/static_content.html``.
Details: templates include
``<%namespace name='static' file='static_content.html'/>``, then
something like ``<%static:css group='application'/>`` to call the
functions in ``common/djangoapps/pipeline_mako/__init__.py``, which call
the ``django-pipeline`` compilers.

Testing
-------

See ``testing.md``.

TODO:
-----

-  describe our production environment

-  describe the front-end architecture, tools, etc. Starting point:
   ``lms/static``

--------------

Note: this file uses markdown. To convert to html, run:

::

    markdown2 overview.md > overview.html



