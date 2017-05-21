# -*- encoding: utf-8

import os
import shutil

from . import css, templates
from .settings import create_new_settings

ROOT = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = '_output'


def create_site(site_dir):
    """Perform the setup for a new site."""
    create_new_settings(site_dir)

    for dirname in ('pages', 'posts', 'static'):
        os.makedirs(dirname, exist_ok=True)

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
