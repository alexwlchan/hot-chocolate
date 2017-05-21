# -*- encoding: utf-8

import os
import shutil


REQUIRED_SETTINGS = {
    'name',
    'url',
    'author',
    'author_email',
    'description',
    'language',
}


class UndefinedSetting(Exception):
    pass


def validate_settings(settings):
    keys = set(settings.keys())
    missing_keys = REQUIRED_SETTINGS - keys
    if missing_keys:
        raise UndefinedSetting(
            f"Missing required settings: {', '.join(missing_keys)}"
        )


def create_new_settings(site_dir):
    """Create a new settings directory in the given directory."""
    shutil.copyfile(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.toml'),
        os.path.join(site_dir, 'settings.toml')
    )
