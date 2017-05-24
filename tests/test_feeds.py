# -*- encoding: utf-8

from datetime import date

import pytest

from hotchocolate import feeds


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
