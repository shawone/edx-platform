# This Python file uses the following encoding: utf-8
"""
This test file will verify proper password policy enforcement, which is an option feature
"""
import json
import uuid

from django.core.urlresolvers import reverse
from mock import patch

from courseware.tests.helpers import LoginEnrollmentTestCase, check_for_post_code

from util.password_validators import (
    override_complexity_settings, override_length_settings, override_dictionary_settings
)


@patch.dict("django.conf.settings.FEATURES", {'USE_PASSWORD_POLICY_ENFORCEMENT': True})
class TestPasswordPolicy(LoginEnrollmentTestCase):
    """
    Go through some password policy tests to make sure things are properly working
    """

    def _do_register_attempt(self, username, email, password):
        """
        Helper method to make the call to the do registration
        """
        resp = check_for_post_code(self, 200, reverse('create_account'), {
            'username': username,
            'email': email,
            'password': password,
            'name': 'username',
            'terms_of_service': 'true',
            'honor_code': 'true',
        })
        data = json.loads(resp.content)
        return data

    def _get_unique_username(self):
        """
        Generate a random username
        """
        return 'foo_bar' + uuid.uuid4().hex

    def _get_unique_email(self):
        """
        Generate a random email address
        """
        return 'foo' + uuid.uuid4().hex + '@bar.com'

    def test_bad_password_length(self):
        """
        Assert that a too short password will fail
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'aaa'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Invalid Length (must be 6 characters or more)")

    def test_good_password_length(self):
        """
        Assert that a longer password will succeed
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'ThisIsALongerPassword'
        )
        self.assertEqual(data['success'], True)

    def test_password_sequence(self):
        """
        Assert that a password with a familiar sequence will fail
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'abcdefg'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Based on a common sequence of characters")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'password'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Based on a common sequence of characters")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            '123456'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Based on a common sequence of characters")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'this_is_not_a_common_sequence'
        )
        self.assertEqual(data['success'], True)

    @override_length_settings(6, 12)
    def test_bad_too_long_password(self):
        """
        Assert that a password that is too long will fail
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'ThisPasswordIsWayTooLong'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Invalid Length (must be 12 characters or less)")

    @override_complexity_settings({'UPPER': 3})
    def test_enough_upper_case_letters(self):
        """
        Assert the rules regarding minimum upper case letters in a password
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'thisshouldfail'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Must be more complex (must contain 3 or more uppercase characters)")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'ThisShouldPass'
        )
        self.assertEqual(data['success'], True)

    @override_complexity_settings({'LOWER': 3})
    def test_enough_lower_case_letters(self):
        """
        Assert the rules regarding minimum lower case letters in a password
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'THISSHOULDFAIL'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Must be more complex (must contain 3 or more lowercase characters)")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'ThisShouldPass'
        )
        self.assertEqual(data['success'], True)

    @override_complexity_settings({'DIGITS': 3})
    def test_enough_digits(self):
        """
        Assert the rules regarding minimum lower case letters in a password
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'thishasnodigits'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Must be more complex (must contain 3 or more digits)")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'Th1sSh0uldPa88'
        )
        self.assertEqual(data['success'], True)

    @override_complexity_settings({'PUNCTUATION': 3})
    def test_enough_punctuations(self):
        """
        Assert the rules regarding minimum punctuation count in a password
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'thisshouldfail'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Must be more complex (must contain 3 or more punctuation characters)")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'Th!sSh.uldPa$*'
        )
        print 'result = {0}'.format(data)
        self.assertEqual(data['success'], True)

    @override_complexity_settings({'WORDS': 3})
    def test_enough_words(self):
        """
        Assert the rules regarding minimum word count in password
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'thisshouldfail'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Must be more complex (must contain 3 or more unique words)")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            u'this should pass'
        )
        self.assertEqual(data['success'], True)

    @override_complexity_settings({'PUNCTUATION': 3})
    @override_complexity_settings({'WORDS': 3})
    @override_complexity_settings({'DIGITS': 3})
    @override_complexity_settings({'LOWER': 3})
    @override_complexity_settings({'UPPER': 3})
    def test_multiple_errors(self):
        """
        Make sure we assert against all violations
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'thisshouldfail'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(
            data['value'],
            "Password: Must be more complex ("
            "must contain 3 or more uppercase characters, "
            "must contain 3 or more digits, "
            "must contain 3 or more punctuation characters, "
            "must contain 3 or more unique words"
            ")"
        )

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            u'tH1s Sh0u!d P3#$'
        )
        self.assertEqual(data['success'], True)

    @override_length_settings(2, 12)
    @override_dictionary_settings(['foo', 'bar'])
    def test_dictionary_similarity(self):
        """
        Assert that passwords should not be too similar to a set of words
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'foo'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Based on a dictionary word.")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            'bar'
        )
        self.assertEqual(data['success'], False)
        self.assertEqual(data['value'], "Password: Based on a dictionary word.")

        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            u'this_is_ok'
        )
        self.assertEqual(data['success'], True)

    def test_with_unicode(self):
        """
        Make sure the library we are using is OK with unicode characters
        """
        data = self._do_register_attempt(
            self._get_unique_username(),
            self._get_unique_email(),
            u'四節比分和七年前'
        )
        self.assertEqual(data['success'], True)
