# -*- encoding: utf-8 -*-
"""
Builds the content feeds.

This file presents functions for building several different feeds: Atom, RSS
and JSON Feed.  All three feed types are build for sites using Hot Chocolate.

"""

import os

import jinja2

from . import templates


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
