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


def build_atom_feed(site, posts):
    """
    Given a list of posts, return a rendered Atom feed.
    """
    template = get_feed_template('atom.xml')
    for post in posts:
        post.metadata['tag_uri'] = get_tag_uri(
            url=site.settings['url'] + post.metadata['slug'],
            date=post.metadata['date']
        )
    atom_xml = template.render(
        site=site,
        posts=posts[:MAX_POSTS],
        updated_date=str(datetime.now())
    )
    return utils.minify_xml(atom_xml.encode('utf8'))
