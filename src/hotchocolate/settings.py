# -*- encoding: utf-8

import os
import shutil

import toml


SETTINGS_NAME = 'settings.toml'

REQUIRED_SETTINGS = {
    'name',
    'url',
    'author',
    'author_email',
    'description',
    'language',
}


def _settings_path(site_dir):
    return os.path.join(site_dir, SETTINGS_NAME)


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
        os.path.join(_settings_path(os.path.dirname(os.path.abspath(__file__)))),
        os.path.join(site_dir, 'settings.toml')
    )


def load_settings(site_dir):
    """Loads the settings from a given directory."""
    path = _settings_path(site_dir)
    return toml.loads(open(path).read())['hotchocolate']
