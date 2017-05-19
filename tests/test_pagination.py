# -*- encoding: utf-8
"""
Tests for the pagination object.
"""

import pytest

from hotchocolate import Pagination


POSTS = ['post_%d' % i for i in range(1, 21)]


@pytest.mark.parametrize('idx, pageset', [
    (0, {
        'slug': '/',
        'articles': POSTS[:5],
        'next': '/page/2/',
        'prev': None,
    }),
    (1, {
        'slug': '/page/2/',
        'articles': POSTS[5:10],
        'next': '/page/3/',
        'prev': '/',
    }),
    (2, {
        'slug': '/page/3/',
        'articles': POSTS[10:15],
        'next': '/page/4/',
        'prev': '/page/2/',
    }),
    (3, {
        'slug': '/page/4/',
        'articles': POSTS[15:20],
        'next': None,
        'prev': '/page/3/',
    }),
])
def test_index_page_pagination(idx, pageset):
    """
    Test the pagination object on the index page.
    """
    pagination = Pagination(posts=POSTS, page_size=5, prefix='')
    pagesets = list(pagination)
    assert pagesets[idx] == pageset


@pytest.mark.parametrize('idx, pageset', [
    (0, {
        'slug': '/tag/',
        'articles': POSTS[:5],
        'next': '/tag/2/',
        'prev': None,
    }),
    (1, {
        'slug': '/tag/2/',
        'articles': POSTS[5:10],
        'next': '/tag/3/',
        'prev': '/tag/',
    }),
    (2, {
        'slug': '/tag/3/',
        'articles': POSTS[10:15],
        'next': '/tag/4/',
        'prev': '/tag/2/',
    }),
    (3, {
        'slug': '/tag/4/',
        'articles': POSTS[15:20],
        'next': None,
        'prev': '/tag/3/',
    }),
])
def test_tag_page_pagination(idx, pageset):
    """
    Test the pagination object on a tag page.
    """
    pagination = Pagination(posts=POSTS, page_size=5, prefix='tag')
    pagesets = list(pagination)
    assert pagesets[idx] == pageset
