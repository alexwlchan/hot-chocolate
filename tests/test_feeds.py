# -*- encoding: utf-8

from datetime import date

import pytest

from hotchocolate import Post, Site, feeds


@pytest.mark.parametrize('url, date, expected_tag_uri', [
    ('http://example.org', None, 'tag:example.org:'),
    ('http://example.org', date(2017, 5, 24), 'tag:example.org,2017-05-24:'),
    ('http://example.org/path/to/page', None, 'tag:example.org:/path/to/page'),
    ('http://example.org/path/to/page', date(2017, 5, 24), 'tag:example.org,2017-05-24:/path/to/page'),
    ('http://example.org/path/to/page#fragment', None, 'tag:example.org:/path/to/page/fragment'),
    ('http://example.org/path/to/page#fragment', date(2017, 5, 24), 'tag:example.org,2017-05-24:/path/to/page/fragment'),
])
def test_get_tag_uri(url, date, expected_tag_uri):
    assert feeds.get_tag_uri(url=url, date=date) == expected_tag_uri


@pytest.mark.parametrize('max_posts', [1, 3, 10, 20])
def test_max_posts_value_is_respected(settings_dict, example_post, max_posts):
    feed_xml = feeds.build_atom_feed(
        site=Site(settings=settings_dict),
        posts=[example_post] * 50,
        max_posts=max_posts
    )
    assert feed_xml.count('<entry>') == max_posts


def test_posts_are_sorted_in_correct_order(settings_dict, example_post):
    site = Site(settings=settings_dict)
    posts = [example_post] * 10
    posts.append(Post(
        path='/dev/null',
        content='A much newer post',
        metadata={
            'date': '3016-07-21',
            'title': 'Hello future world'
        }
    ))
    feed_xml = feeds.build_atom_feed(
        site=site,
        posts=posts,
        max_posts=5
    )

    assert 'Hello future world' in feed_xml


def test_optional_tags_are_omitted_by_default(settings_dict, example_post):
    site = Site(settings=settings_dict)
    feed_xml = feeds.build_atom_feed(
        site=site,
        posts=[example_post]
    )

    # There's an <updated> tag at the top of the feed, but we don't want
    # it in the entries.
    assert feed_xml.count('<updated>') == 1

    assert '</summary>' not in feed_xml


def test_updated_date_is_included(settings_dict, example_post):
    site = Site(settings=settings_dict)
    example_post.metadata['date_updated'] = '2016-07-22'
    feed_xml = feeds.build_atom_feed(
        site=site,
        posts=[example_post]
    )

    # Once at the top of the feed, once in the entry.
    assert feed_xml.count('<updated>') == 2


def test_updated_date_is_included(settings_dict, example_post):
    site = Site(settings=settings_dict)
    example_post.metadata['summary'] = 'A story about snails'
    feed_xml = feeds.build_atom_feed(
        site=site,
        posts=[example_post]
    )

    # Once at the top of the feed, once in the entry.
    assert '</summary>' in feed_xml
