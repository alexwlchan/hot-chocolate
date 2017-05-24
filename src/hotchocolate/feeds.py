# -*- encoding: utf-8 -*-
"""
Builds the content feeds.

This file presents functions for building several different feeds: Atom, RSS
and JSON Feed.  All three feed types are build for sites using Hot Chocolate.

"""

from datetime import datetime
import os
from urllib.parse import urlparse

import jinja2

from . import templates, utils


# How many posts to include in the feeds.
MAX_POSTS = 20


def get_tag_uri(url, date):
    """
    Creates a TagURI.
    See http://web.archive.org/web/20110514113830/http://diveintomark.org/archives/2004/05/28/howto-atom-id
    """
    # Taken from feedgenerator.django.utils.feedgenerator
    bits = urlparse(url)
    d = ''
    if date is not None:
        d = ',%s' % date.strftime('%Y-%m-%d')
    fragment = ''
    if bits.fragment != '':
        fragment = '/%s' % (bits.fragment)
    return 'tag:%s%s:%s%s' % (bits.hostname, d, bits.path, fragment)


def get_feed_template(name):
    """
    Load a template for an XML feed.  If one isn't available in the standard
    templates directory, load from the install directory.
    """
    try:
        env = templates.build_environment()
        return env.get_template(name)
    except jinja2.exceptions.TemplateNotFound:
        env = templates.build_environment(template_dir=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'templates'
        ))
        return env.get_template(name)


def _build_feed(template_name, site, posts, max_posts):
    template = get_feed_template(template_name)
    posts = sorted(posts, key=lambda p: p.metadata['date'], reverse=True)
    for post in posts:
        post.metadata['tag_uri'] = get_tag_uri(
            url=site.settings['url'] + post.metadata['slug'],
            date=post.metadata['date']
        )
    atom_xml = template.render(
        site=site,
        posts=posts[:max_posts],
        updated_date=datetime.now()
    )
    return utils.minify_xml(atom_xml.encode('utf8'))


def build_atom_feed(site, posts, max_posts=MAX_POSTS):
    """Given a list of posts, return a rendered Atom feed."""
    return _build_feed(
        template_name='atom.xml',
        site=site,
        posts=posts,
        max_posts=max_posts
    )


def build_rss_feed(site, posts, max_posts=MAX_POSTS):
    """Given a list of posts, return a rendered RSS feed."""
    return _build_feed(
        template_name='rss.xml',
        site=site,
        posts=posts,
        max_posts=max_posts
    )


def write_all_feeds(output_dir, site, posts, max_posts=MAX_POSTS):
    """Build and write the RSS, Atom and JSON feeds."""
    feed_dir = os.path.join(output_dir, 'feeds')
    os.makedirs(feed_dir, exist_ok=True)

    atom_xml = build_atom_feed(site=site, posts=posts, max_posts=max_posts)
    with open(os.path.join(feed_dir, 'all.atom.xml'), 'w') as f:
        f.write(atom_xml)

    rss_xml = build_rss_feed(site=site, posts=posts, max_posts=max_posts)
    with open(os.path.join(feed_dir, 'rss.xml'), 'w') as f:
        f.write(rss_xml)

