"""
Unittests for importing a course via management command
"""

import os
from path import path
import shutil
import tempfile

from django.core.management import call_command
from django.test.utils import override_settings

from contentstore.tests.modulestore_config import TEST_MODULESTORE
from django_comment_common.utils import are_permissions_roles_seeded
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase


@override_settings(MODULESTORE=TEST_MODULESTORE)
class TestImport(ModuleStoreTestCase):
    """
    Unit tests for importing a course from command line
    """

    COURSE_ID = ['EDx', '0.00x', '2013_Spring', ]
    DIFF_RUN = ['EDx', '0.00x', '2014_Spring', ]

    def setUp(self):
        """
        Build course XML for importing
        """
        super(TestImport, self).setUp()
        self.content_dir = path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.content_dir)

        # Create good course xml
        self.good_dir = tempfile.mkdtemp(dir=self.content_dir)
        os.makedirs(os.path.join(self.good_dir, "course"))
        with open(os.path.join(self.good_dir, "course.xml"), "w+") as f:
            f.write('<course url_name="{0[2]}" org="{0[0]}" '
                    'course="{0[1]}"/>'.format(self.COURSE_ID))

        with open(os.path.join(self.good_dir, "course", "{0[2]}.xml".format(self.COURSE_ID)), "w+") as f:
            f.write('<course></course>')

        # Create run changed course xml
        self.dupe_dir = tempfile.mkdtemp(dir=self.content_dir)
        os.makedirs(os.path.join(self.dupe_dir, "course"))
        with open(os.path.join(self.dupe_dir, "course.xml"), "w+") as f:
            f.write('<course url_name="{0[2]}" org="{0[0]}" '
                    'course="{0[1]}"/>'.format(self.DIFF_RUN))

        with open(os.path.join(self.dupe_dir, "course", "{0[2]}.xml".format(self.DIFF_RUN)), "w+") as f:
            f.write('<course></course>')

    def test_forum_seed(self):
        """
        Tests that forum roles were created with import.
        """
        self.assertFalse(are_permissions_roles_seeded('/'.join(self.COURSE_ID)))
        call_command('import', self.content_dir, self.good_dir)
        self.assertTrue(are_permissions_roles_seeded('/'.join(self.COURSE_ID)))

    def test_duplicate_with_url(self):
        """
        Check to make sure an import doesn't import courses that have the
        same org and course, but they have different runs in order to
        prevent modulestore "findone" exceptions on deletion
        """
        # Load up base course and verify it is available
        call_command('import', self.content_dir, self.good_dir)
        store = modulestore()
        self.assertIsNotNone(store.get_course('/'.join(self.COURSE_ID)))

        # Now load up duped course and verify it doesn't load
        call_command('import', self.content_dir, self.dupe_dir)
        self.assertIsNone(store.get_course('/'.join(self.DIFF_RUN)))
