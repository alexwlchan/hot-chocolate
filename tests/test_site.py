# -*- encoding: utf-8

import pytest

from hotchocolate import site


def test_create_site_builds_right_directories(tmpdir):
    site.create_site(str(tmpdir))
    for dirname in ['pages', 'posts', 'static', 'styles', 'templates']:
        assert tmpdir.join(dirname).exists()
    assert tmpdir.join('settings.toml').exists()
