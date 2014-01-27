"""
Course about page (with registration button)
"""

from .course_page import CoursePage


class CourseAboutPage(CoursePage):
    """
    Course about page (with registration button)
    """

    URL_PATH = "about"

    def is_browser_on_page(self):
        return self.is_css_present('section.course-info')

    def register(self):
        """
        Register for the course on the page.
        """
        self.css_click('a.register')
        self.ui.wait_for_page('lms.register')
