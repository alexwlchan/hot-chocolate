# -*- encoding: utf-8
"""
Tests for the CSS helpers.
"""

import pytest

from hotchocolate import css


@pytest.mark.parametrize('method', [css.cleancss, css.optimize])
@pytest.mark.parametrize('css_string', [
    'p { color: red; }',
])
def test_processor_does_not_lengthen_output(method, css_string):
    """
    All of the CSS processors should return CSS that is no longer than the
    input they're passed.
    """
    assert len(method(css_string)) <= len(css_string)
