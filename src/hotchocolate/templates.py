# -*- encoding: utf-8
"""
Provides template utilities.
"""

import functools

import jinja2

from . import markdown as md, plugins

# TODO: Make this a setting
TEMPLATE_DIR = 'templates'


# TODO: Make this a setting
def locale_date(date):
    """Render a date in the current locale date."""
    return date.strftime('%d %B %Y').lstrip('0')


@functools.lru_cache()
def render_title(title):
    return md.convert_markdown(
        title,
        extra_extensions=plugins.load_markdown_extensions(),
        parse_metadata=False
    ).replace('<p>', '').replace('</p>', '')


def build_environment(template_dir=None):
    """Build the appropriate Jinja2 environment."""
    if template_dir is None:
        template_dir = TEMPLATE_DIR
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html']),
        undefined=jinja2.StrictUndefined
    )

    # TODO: Extension mechanism for additional filters?
    env.filters['locale_date'] = locale_date
    env.filters['title'] = render_title

    return env
