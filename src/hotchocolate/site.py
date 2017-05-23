# -*- encoding: utf-8

import os
import shutil

import bs4
import htmlmin

from . import css, templates
from .settings import create_new_settings

ROOT = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = '_output'


def create_site(site_dir):
    """Perform the setup for a new site."""
    create_new_settings(site_dir)

    for dirname in ('pages', 'posts', 'static'):
        os.makedirs(os.path.join(site_dir, dirname), exist_ok=True)

    for dirname in [css.STYLE_DIR, templates.TEMPLATE_DIR]:
        shutil.copytree(
            os.path.join(ROOT, dirname),
            os.path.join(site_dir, dirname)
        )


def clean_site(site_dir):
    """Delete all the generated output."""
    try:
        shutil.rmtree(OUTPUT_DIR)
    except FileNotFoundError:
        pass


class NewSite:
    """
    Mixin class containing refactored methods from the ``Site`` class
    in ``__init__.py``.
    """
    def add_css_to_html(self, css_string):
        """Insert CSS into all the rendered HTML pages."""
        for slug, html_str in self._prepared_html.items():

            # Find the body text for this page -- i.e., the HTML we want
            # to compare the CSS with.
            soup = bs4.BeautifulSoup(html_str, 'html.parser')
            body_html = ''.join([str(s) for s in soup.find('body').contents])

            min_css = css.minimal_css_for_html(
                body_html=body_html, css=css_string
            )

            # Add the CSS within the <head> section.  If there isn't one,
            # add it.
            if min_css.strip():
                if '</head>' not in html_str:
                    html_str = html_str.replace('<body', '<head></head><body', 1)
                html_str = html_str.replace(
                    '</head>', f'<style>{min_css}</style></head>'
                )

            self._prepared_html[slug] = html_str

    def optimise_html(self):
        """Minify the HTML and prepare it for writing to disk."""
        for slug, html_str in self._prepared_html.items():
            html_str = htmlmin.minify(html_str)
            self._prepared_html[slug] = html_str
