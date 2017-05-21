# -*- encoding: utf-8

import copy
import os

import pytest

from hotchocolate import settings


def test_valid_settings_are_allowed(settings_dict):
    settings.validate_settings(settings_dict)


@pytest.mark.parametrize('fields', [
    ('name', ),
    ('name', 'url', ),
    ('url', ),
    ('author', 'author_email'),
    ('description', ),
    ('language', ),
])
def test_invalid_settings_are_rejected(settings_dict, fields):
    new_settings = {s: v for s, v in settings_dict.items() if s not in fields}
    with pytest.raises(settings.UndefinedSetting):
        settings.validate_settings(new_settings)


def test_can_create_new_settings_file(tmpdir):
    site_dir = str(tmpdir)
    settings_path = os.path.join(site_dir, 'settings.toml')
    assert not os.path.exists(settings_path)
    settings.create_new_settings(site_dir=site_dir)
    assert os.path.exists(settings_path)
