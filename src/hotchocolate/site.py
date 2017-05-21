# -*- encoding: utf-8

import os
import shutil

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
            # TODO: Replace this with a proper parser for extracting the HTML.
            # TODO: Remove all other <style> tags.
            body_html = html_str.split('<body>')[1].split('</body>')[0]
            min_css = css.minimal_css_for_html(body_html=body_html, css=css_string)

            html_str = html_str.replace(
                '<!-- hc_css_include -->', f'<style>{min_css}</style>'
            )

            # If there's no CSS, we can just drop the <style> tag.
            html_str = html_str.replace('<style></style>', '')

            self._prepared_html[slug] = html_str

    def optimise_html(self):
        """Minify the HTML and prepare it for writing to disk."""
        for slug, html_str in self._prepared_html.items():
            html_str = htmlmin.minify(html_str)
            self._prepared_html[slug] = html_str
