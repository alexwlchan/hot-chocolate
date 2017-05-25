# -*- encoding: utf-8 -*-

import string

from hypothesis import example, given
from hypothesis.strategies import text
import pytest

from hotchocolate import utils


@pytest.mark.parametrize('xml_string, minified_string', [
    (
        '<root>  <a/>   <b>  </b>     </root>',
        '<root><a/><b/></root>'
    ),
    (
        '<root>  <a/>   <b>data</b>     </root>',
        '<root><a/><b>data</b></root>'
    ),
])
def test_xml_minify(xml_string, minified_string):
    assert utils.minify_xml(xml_string) == minified_string


def test_chunks():
    x = list(range(10))
    expected_chunks = [
        [0, 1], [2, 3], [4, 5], [6, 7], [8, 9]
    ]
    for expected, actual in zip(expected_chunks, utils.chunks(x, 2)):
        assert expected == actual


class TestSlugify:

    @given(text(min_size=1))
    def test_character_whitelist(self, xs):
        result = utils.slugify(xs)
        allowed_chars = string.ascii_lowercase + string.digits + '-'
        assert all(x in allowed_chars for x in result)

    @given(text(min_size=1))
    def test_slugify_is_lowercase(self, xs):
        result = utils.slugify(xs)
        assert result == result.lower()

    @example('hello  world')
    @given(text(min_size=1))
    def test_no_repeated_hyphens(self, xs):
        assert '--' not in utils.slugify(xs)
