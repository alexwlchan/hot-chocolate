# -*- encoding: utf-8
"""
Tests for the CSS helpers.
"""

from hotchocolate import css


def test_cleancss_does_not_lengthen_output():
    """
    We can't guarantee that cleancss is installed or available in tests (yet),
    so for now just test that it never causes length to increase.
    """
    css_string = 'p { color: red; }'
    assert len(css.cleancss(css_string)) <= len(css_string)
