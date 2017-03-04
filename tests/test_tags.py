# -*- encoding: utf-8

from bs4 import BeautifulSoup
import pytest

import os


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
    tag_inner = html.find(id='article_tags').contents[0]
    assert not tag_inner.rstrip().endswith(',')
