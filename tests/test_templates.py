# -*- encoding: utf-8

import datetime

from jinja2 import Environment
import pytest

from hotchocolate import templates


@pytest.mark.parametrize('date, date_string', [
    (datetime.date(2000, 1, 1), '1 January 2000'),
    (datetime.date(2017, 12, 31), '31 December 2017'),
])
def test_locale_date(date, date_string):
    assert templates.locale_date(date) == date_string


def test_environment_is_right_type():
    assert isinstance(templates.build_environment(), Environment)


def test_environment_with_custom_dir_is_right_type():
    assert isinstance(
        templates.build_environment(template_dir='custom_dir'),
        Environment)
