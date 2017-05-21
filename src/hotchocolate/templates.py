# -*- encoding: utf-8
"""
Provides template utilities.
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape

# TODO: Make this a setting
TEMPLATE_DIR = 'templates'


# TODO: Make this a setting
def locale_date(date):
    """
    Render a date in the current locale date.
    """
    return date.strftime('%-d %B %Y')


def build_environment(template_dir=None):
    """
    Build the appropriate Jinja2 environment.
    """
    if template_dir is None:
        template_dir = TEMPLATE_DIR
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html'])
    )

    # TODO: Extension mechanism for additional filters?
    env.filters['locale_date'] = locale_date

    return env
