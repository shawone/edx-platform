"""
Base class for pages in courseware.
"""

from bok_choy.page_object import PageObject
from . import BASE_URL


class CoursePage(PageObject):
    """
    Abstract base class for page objects within a course.
    """

    # Overridden by subclasses to provide the relative path within the course
    # Does not need to include the leading forward slash.
    URL_PATH = ""

    def __init__(self, browser, course_id):
        """
        Course ID is currently of the form "edx/999/2013_Spring"
        but this format could change.
        """
        super(CoursePage, self).__init__(browser)
        self.course_id = course_id

    @property
    def url(self):
        """
        Construct a URL to the page within the course.
        """
        return BASE_URL + "/courses/" + self.course_id + "/" + self.URL_PATH
