# -*- encoding: utf-8
"""
Tests for the CSS helpers.
"""

import os

import pytest

from hotchocolate import css


@pytest.mark.parametrize('method', [css.cleancss, css.optimize_css])
@pytest.mark.parametrize('css_string', [
    'p { color: red; }',
])
def test_processor_does_not_lengthen_output(method, css_string):
    """
    All of the CSS processors should return CSS that is no longer than the
    input they're passed.
    """
    assert len(method(css_string)) <= len(css_string)


@pytest.mark.parametrize('body_html, input_css, expected_css', [
    (
        '<p>A paragraph about a parrot</p>',
        'p { color: red; }',
        'p { color: red; }'
    ),
    (
        '<p>A paragraph about a parrot</p>',
        'p { color: red; } b { color: yellow; }',
        'p { color: red; }'
    ),
    (
        '<p>A paragraph about a parrot</p>',
        'p { color: red; } @media (screen and max-width: 500px) {p { color: yellow; }}',
        'p { color: red; } @media (screen and max-width: 500px) {p { color: yellow; }}'
    ),
])
def test_minimal_css_for_html(body_html, input_css, expected_css):
    result = css.minimal_css_for_html(body_html=body_html, css=input_css)
    assert result == expected_css


def test_load_base_css_with_custom_style_dir(test_root):
    style_dir = os.path.join(test_root, css.STYLE_DIR)
    result = css.load_base_css(style_dir=style_dir)
    assert result == 'p {\n  color: red; }\n'


def test_load_base_css_with_default_dir(test_root):
    curdir = os.curdir
    os.chdir(test_root)
    result = css.load_base_css()
    os.chdir(curdir)
    assert result == 'p {\n  color: red; }\n'
