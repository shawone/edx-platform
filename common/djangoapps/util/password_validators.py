"""
This file exposes a number of password complexity validators which can be optionally added to
account creation

This file is taken from the django-passwords project at https://github.com/dstufft/django-passwords
authored by dstufft (https://github.com/dstufft) and released under BSD license
"""
from __future__ import division
import string  # pylint: disable=W0402

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.conf import settings
from django.utils.functional import wraps

COMMON_SEQUENCES = [
    "0123456789",
    "`1234567890-=",
    "~!@#$%^&*()_+",
    "abcdefghijklmnopqrstuvwxyz",
    "quertyuiop[]\\asdfghjkl;\'zxcvbnm,./",
    'quertyuiop{}|asdfghjkl;"zxcvbnm<>?',
    "quertyuiopasdfghjklzxcvbnm",
    "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\",
    "qazwsxedcrfvtgbyhnujmikolp",
    "password"
]

# Settings
PASSWORD_MIN_LENGTH = getattr(settings, "PASSWORD_MIN_LENGTH", 6)
PASSWORD_MAX_LENGTH = getattr(settings, "PASSWORD_MAX_LENGTH", None)
PASSWORD_DICTIONARY = getattr(settings, "PASSWORD_DICTIONARY", None)
PASSWORD_MATCH_THRESHOLD = getattr(settings, "PASSWORD_MATCH_THRESHOLD", 0.9)
PASSWORD_COMMON_SEQUENCES = getattr(settings, "PASSWORD_COMMON_SEQUENCES", COMMON_SEQUENCES)
PASSWORD_COMPLEXITY = getattr(settings, "PASSWORD_COMPLEXITY", None)


class LengthValidator(object):
    """
    Validator that enforces minimum length of a password
    """
    message = _("Invalid Length (%s)")
    code = "length"

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(
                self.message % _("must be %s characters or more") % self.min_length,
                code=self.code)
        elif self.max_length and len(value) > self.max_length:
            raise ValidationError(
                self.message % _("must be %s characters or less") % self.max_length,
                code=self.code)


class ComplexityValidator(object):
    """
    Validator that enforces minimum complexity
    """
    message = _("Must be more complex (%s)")
    code = "complexity"

    def __init__(self, complexities):
        self.complexities = complexities

    def __call__(self, value):
        if self.complexities is None:
            return

        uppercase, lowercase, digits, non_ascii, punctuation = set(), set(), set(), set(), set()

        for character in value:
            if character.isupper():
                uppercase.add(character)
            elif character.islower():
                lowercase.add(character)
            elif character.isdigit():
                digits.add(character)
            elif character in string.punctuation:
                punctuation.add(character)
            else:
                non_ascii.add(character)

        words = set(value.split())

        errors = []
        if len(uppercase) < self.complexities.get("UPPER", 0):
            errors.append(_("must contain %(UPPER)s or more uppercase characters") % self.complexities)
        if len(lowercase) < self.complexities.get("LOWER", 0):
            errors.append(_("must contain %(LOWER)s or more lowercase characters") % self.complexities)
        if len(digits) < self.complexities.get("DIGITS", 0):
            errors.append(_("must contain %(DIGITS)s or more digits") % self.complexities)
        if len(punctuation) < self.complexities.get("PUNCTUATION", 0):
            errors.append(_("must contain %(PUNCTUATION)s or more punctuation characters") % self.complexities)
        if len(non_ascii) < self.complexities.get("NON ASCII", 0):
            errors.append(_("must contain %(NON ASCII)s or more non ascii characters") % self.complexities)
        if len(words) < self.complexities.get("WORDS", 0):
            errors.append(_("must contain %(WORDS)s or more unique words") % self.complexities)

        if errors:
            raise ValidationError(self.message % (u', '.join(errors),), code=self.code)


class BaseSimilarityValidator(object):
    """
    Base class which is used to make sure passwords aren't too similar to words in a dictionary
    """
    message = _("Too Similar to [%(haystacks)s]")
    code = "similarity"

    def __init__(self, haystacks=None):
        self.haystacks = haystacks if haystacks else []

    def fuzzy_substring(self, needle, haystack):
        """
        Perform fuzzy matching of a word within a collection of words
        """
        needle, haystack = needle.lower(), haystack.lower()
        len_m, len_n = len(needle), len(haystack)

        if len_m == 1:
            if not needle in haystack:
                return -1
        if not len_n:
            return len_m

        row1 = [0] * (len_n + 1)
        for i in xrange(0, len_m):
            row2 = [i + 1]
            for j in xrange(0, len_n):
                cost = (needle[i] != haystack[j])
                row2.append(min(row1[j + 1] + 1, row2[j] + 1, row1[j] + cost))
            row1 = row2
        return min(row1)

    def __call__(self, value):
        for haystack in self.haystacks:
            distance = self.fuzzy_substring(value, haystack)
            longest = max(len(value), len(haystack))
            similarity = (longest - distance) / longest
            if similarity >= PASSWORD_MATCH_THRESHOLD:
                raise ValidationError(
                    self.message % {"haystacks": ", ".join(self.haystacks)},
                    code=self.code)


class DictionaryValidator(BaseSimilarityValidator):
    """
    Validator which enforces that passwords are not too similar to a passed in dictionary
    """
    message = _("Based on a dictionary word.")
    code = "dictionary_word"

    def __init__(self, words=None, dictionary=None):
        haystacks = []
        if dictionary:
            with open(dictionary) as dictionary:
                haystacks.extend(
                    [smart_unicode(x.strip()) for x in dictionary.readlines()]
                )
        if words:
            haystacks.extend(words)
        super(DictionaryValidator, self).__init__(haystacks=haystacks)


class CommonSequenceValidator(BaseSimilarityValidator):
    """
    Validator which enforces that passwords are not too similar to a preset list of common sequences of characters
    """
    message = _("Based on a common sequence of characters")
    code = "common_sequence"

password_validate_length = LengthValidator(PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH)  # pylint: disable=C0103
password_validate_complexity = ComplexityValidator(PASSWORD_COMPLEXITY)  # pylint: disable=C0103
password_validate_dictionary_words = DictionaryValidator(dictionary=PASSWORD_DICTIONARY)  # pylint: disable=C0103
password_validate_common_sequences = CommonSequenceValidator(PASSWORD_COMMON_SEQUENCES)  # pylint: disable=C0103


class override_length_settings(object):  # pylint: disable=C0103
    """
    Allows for overrides during password complexity testing
    """
    def __init__(self, min_length, max_length):
        """
        Initializer
        """
        self.min_length = min_length
        self.max_length = max_length

    def __enter__(self):
        """
        Required entry point for decorators
        """
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Required entry point for decorators
        """
        pass

    def __call__(self, func):
        """
        Invoked when function is called
        """
        decorator_self = self

        @wraps(func)
        def test_wrapping(*args, **kwargs):
            existing_min_length = password_validate_length.min_length
            existing_max_length = password_validate_length.max_length

            password_validate_length.min_length = decorator_self.min_length
            password_validate_length.max_length = decorator_self.max_length

            try:
                with self:
                    func(*args, **kwargs)
            finally:
                password_validate_length.min_length = existing_min_length
                password_validate_length.max_length = existing_max_length

        return test_wrapping


class override_complexity_settings(object):  # pylint: disable=C0103
    """
    Allows for overrides during password complexity testing
    """
    def __init__(self, overrides):
        """
        Initializer
        """
        self.overrides = overrides

    def __enter__(self):
        """
        Required entry point for decorators
        """
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Required entry point for decorators
        """
        pass

    def __call__(self, func):
        """
        Invoked when function is called
        """
        decorator_self = self

        @wraps(func)
        def test_wrapping(*args, **kwargs):

            # keep track of existing values
            existing = {}
            if password_validate_complexity.complexities:
                for key in decorator_self.overrides:
                    existing[key] = password_validate_complexity.complexities.get(key)
            else:
                password_validate_complexity.complexities = {}

            # now apply overrides
            for key in self.overrides:
                password_validate_complexity.complexities[key] = self.overrides[key]

            try:
                with self:
                    func(*args, **kwargs)
            finally:
                # put back original values
                if existing:
                    for key in existing:
                        if existing[key]:
                            password_validate_complexity.complexities[key] = existing[key]
                        else:
                            del password_validate_complexity.complexities[key]
                else:
                    password_validate_complexity.complexities = None
        return test_wrapping


class override_dictionary_settings(object):  # pylint: disable=C0103
    """
    Allows for overrides during password complexity testing
    """
    def __init__(self, haystacks):
        """
        Initializer
        """
        self.haystacks = haystacks

    def __enter__(self):
        """
        Required entry point for decorators
        """
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Required entry point for decorators
        """
        pass

    def __call__(self, func):
        """
        Invoked when function is called
        """
        decorator_self = self

        @wraps(func)
        def test_wrapping(*args, **kwargs):
            existing_haystacks = password_validate_dictionary_words.haystacks

            password_validate_dictionary_words.haystacks = decorator_self.haystacks
            try:
                with self:
                    func(*args, **kwargs)
            finally:
                password_validate_dictionary_words.haystacks = existing_haystacks

        return test_wrapping
