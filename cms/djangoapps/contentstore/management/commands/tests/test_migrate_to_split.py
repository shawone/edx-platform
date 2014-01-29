"""
Unittests for importing a course via management command
"""
import unittest

from django.core.management import CommandError, call_command
from django.test.utils import override_settings
from contentstore.management.commands.migrate_to_split import Command
from contentstore.tests.modulestore_config import TEST_MODULESTORE
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from student.tests.factories import UserFactory
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.django import loc_mapper


class TestArgParsing(unittest.TestCase):
    def setUp(self):
        self.command = Command()

    def test_no_args(self):
        errstring = "migrate_to_split requires at least two arguments"
        with self.assertRaisesRegexp(CommandError, errstring):
            self.command.handle()

    def test_invalid_location(self):
        errstring = "Invalid location string"
        with self.assertRaisesRegexp(CommandError, errstring):
            self.command.handle("foo", "bar")

    def test_nonexistant_user_id(self):
        errstring = "No user exists with ID 99"
        with self.assertRaisesRegexp(CommandError, errstring):
            self.command.handle("i4x://org/course/category/name", "99")

    def test_nonexistant_user_email(self):
        errstring = "No user exists with email fake@example.com"
        with self.assertRaisesRegexp(CommandError, errstring):
            self.command.handle("i4x://org/course/category/name", "fake@example.com")


@override_settings(MODULESTORE=TEST_MODULESTORE)
class TestMigrateToSplit(ModuleStoreTestCase):
    """
    Unit tests for importing a course from command line
    """

    def setUp(self):
        super(TestMigrateToSplit, self).setUp()
        self.course = CourseFactory()
        self.user = UserFactory()

    def test_happy_path(self):
        call_command(
            "migrate_to_split",
            str(self.course.location),
            self.user.email,
        )
        locator = loc_mapper().translate_location(self.course.id, self.course.location)
        course_from_split = modulestore('split').get_course(locator)
        self.assertIsNotNone(course_from_split)
