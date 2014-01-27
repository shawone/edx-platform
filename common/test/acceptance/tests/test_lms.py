"""
E2E tests for the LMS.
"""

from bok_choy.web_app_test import WebAppTest
from bok_choy.promise import EmptyPromise, fulfill_before

from .helpers import UniqueCourseTest
from ..edxapp_pages.lms.login import LoginPage
from ..edxapp_pages.lms.find_courses import FindCoursesPage
from ..edxapp_pages.lms.course_about import CourseAboutPage
from ..edxapp_pages.lms.register import RegisterPage
from ..edxapp_pages.lms.dashboard import DashboardPage
from ..edxapp_pages.lms.course_info import CourseInfoPage
from ..edxapp_pages.lms.tab_nav import TabNavPage
from ..edxapp_pages.lms.course_nav import CourseNavPage
from ..edxapp_pages.lms.progress import ProgressPage
from ..edxapp_pages.lms.video import VideoPage
from ..fixtures.course import CourseFixture


class RegistrationTest(UniqueCourseTest):
    """
    Verify user-facing pages for unregistered users.
    Test the registration process.
    """

    def setUp(self):
        super(RegistrationTest, self).setUp()

        self.find_courses_page = FindCoursesPage(self.browser)
        self.course_about_page = CourseAboutPage(self.browser, self.course_id)

        # Create a course to register for
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        ).install()

    def test_register(self):

        # Visit the main page with the list of courses
        self.find_courses_page.visit()

        # Expect that the demo course exists
        # TODO -- this is failing, not sure why.  Appears that the course id list has something in it, but not what we installed
        course_ids = self.find_courses_page.course_id_list
        self.assertIn(self.course_id, course_ids)

        # Go to the course about page
        self.find_courses_page.go_to_course(self.course_id)

        # Click the register button
        register_page = self.course_about_page.register()

        # Fill in registration info and submit
        username = "test_" + self.unique_id[0:6]
        register_page.provide_info(
            username + "@example.com", "test", username, "Test User"
        )
        register_page.submit()

        # We should end up at the dashboard
        # Check that we're registered for the course
        course_names = self.dashboard.available_courses
        self.assertIn(self.course_info['display_name'], course_names)


class HighLevelTabTest(UniqueCourseTest):
    """
    Tests that verify each of the high-level tabs available within a course.
    """

    def test_course_info(self):
        """
        Navigate to the course info page.
        """
        self.ui['lms.dashboard'].view_course(DEMO_COURSE_ID)

        # Expect just one update
        num_updates = self.ui['lms.course_info'].num_updates()
        self.assertEqual(num_updates, 1)

        # Expect a link to the demo handout pdf
        handout_links = self.ui['lms.course_info'].handout_links()
        self.assertEqual(len(handout_links), 1)
        self.assertIn('demoPDF.pdf', handout_links[0])

    def test_progress(self):
        """
        Navigate to the progress page.
        """
        self.ui['lms.dashboard'].view_course(DEMO_COURSE_ID)
        self.ui['lms.tab_nav'].go_to_tab('Progress')

        # We haven't answered any problems yet, so assume scores are zero
        CHAPTER = 'Example Week 1: Getting Started'
        SECTION = 'Homework - Question Styles'
        EXPECTED_SCORES = [(0, 1), (0, 1), (0, 3), (0, 1), (0, 1), (0, 3), (0, 1)]

        actual_scores = self.ui['lms.progress'].scores(CHAPTER, SECTION)
        self.assertEqual(actual_scores, EXPECTED_SCORES)

    def test_courseware_nav(self):
        """
        Navigate to a particular unit in the courseware.
        """
        self.ui['lms.dashboard'].view_course(DEMO_COURSE_ID)
        self.ui['lms.tab_nav'].go_to_tab('Courseware')

        # Check that the courseware navigation appears correctly
        EXPECTED_SECTIONS = {
            'Introduction': ['Demo Course Overview'],
            'Example Week 1: Getting Started': ['Lesson 1 - Getting Started', 'Homework - Question Styles']
        }
        actual_sections = self.ui['lms.course_nav'].sections
        for section, subsections in EXPECTED_SECTIONS.iteritems():
            self.assertIn(section, actual_sections)
            self.assertEqual(actual_sections[section], EXPECTED_SECTIONS[section])

        # Navigate to a particular section
        self.ui['lms.course_nav'].go_to_section(
            'Example Week 1: Getting Started', 'Homework - Question Styles'
        )

        # Check the sequence items
        EXPECTED_ITEMS = [
            'Pointing on a Picture', 'Drag and Drop', 'Multiple Choice Questions',
            'Mathematical Expressions', 'Chemical Equations', 'Numerical Input', 'Text Input'
        ]

        actual_items = self.ui['lms.course_nav'].sequence_items
        self.assertEqual(len(actual_items), len(EXPECTED_ITEMS))
        for expected in EXPECTED_ITEMS:
            self.assertIn(expected, actual_items)

    def test_video_player(self):
        """
        Play a video in the courseware.
        """

        # Navigate to a video in the demo course
        self.ui['lms.dashboard'].view_course(DEMO_COURSE_ID)
        self.ui['lms.tab_nav'].go_to_tab('Courseware')
        self.ui['lms.course_nav'].go_to_section('Introduction', 'Demo Course Overview')

        # The video should start off paused
        # Since the video hasn't loaded yet, it's elapsed time and duration are both 0
        self.assertFalse(self.ui['lms.video'].is_playing)
        self.assertEqual(self.ui['lms.video'].duration, 0)
        self.assertEqual(self.ui['lms.video'].elapsed_time, 0)

        # Play the video
        self.ui['lms.video'].play()

        # Now we should be playing
        self.assertTrue(self.ui['lms.video'].is_playing)

        # Wait for the video to load the duration
        # We *should* wait for the video's elapsed time to increase,
        # but SauceLabs has difficulty downloading the full video through
        # the ssh tunnel.
        video_duration_loaded = EmptyPromise(
            lambda: self.ui['lms.video'].duration == 194,
            'video has duration', timeout=20
        )

        with fulfill_before(video_duration_loaded):

            # Pause the video
            self.ui['lms.video'].pause()

            # Expect that the elapsed time and duration are reasonable
            # Again, we can't expect the video to actually play because of
            # latency through the ssh tunnel
            self.assertGreaterEqual(self.ui['lms.video'].elapsed_time, 0)
            self.assertEqual(self.ui['lms.video'].duration, 194)

    def _login(self):
        """
        Log in as the test user and navigate to the dashboard,
        where we should see the demo course.
        """
        self.ui.visit('lms.login')
        self.ui['lms.login'].login(self.email, self.password)
        course_names = self.ui['lms.dashboard'].available_courses()
        self.assertIn(DEMO_COURSE_TITLE, course_names)
