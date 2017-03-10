# -*- encoding: utf-8

from bs4 import BeautifulSoup
import pytest

import os

from hotchocolate import Article


# TOOD: Move this into a utils.py
def output_soup(path):
    abspath = os.path.join('tests/examplesite/_output', path, 'index.html')
    html = open(abspath).read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup


@pytest.mark.parametrize('html', [
    output_soup('2017/03/a-post-with-two-tags/'),
    output_soup('2017/03/a-post-with-four-tags/'),
])
def test_tag_links_dont_have_a_trailing_comma(html):
    """
    The list of tags in an article doesn't end with a trailing comma.
    """
    tag_inner = html.findAll('li', {'class': 'article_tags'})[0].contents[0]
    assert not tag_inner.rstrip().endswith(',')


@pytest.mark.parametrize('tag_string, expected', [
    ('python,', ['python']),
    ('python, foo,', ['foo', 'python']),
    ('trailing, whitespace,  ', ['trailing', 'whitespace']),
])
def test_tag_metadata_with_trailing_comma_is_stripped(tag_string, expected):
    """
    If there's a trailing comma on tag metadata, we don't get an empty tag.

    This is based on a real example I saw.
    """
    article = Article(
        content='hello world',
        metadata={
            'tags': tag_string,
            'title': 'A title for testing'
        },
        path=None)
    assert article.tags == expected
