# -*- encoding: utf-8

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
