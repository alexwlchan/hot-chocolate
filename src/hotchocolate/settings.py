# -*- encoding: utf-8

from configparser import ConfigParser, NoOptionError, NoSectionError
import collections
import os


DEFAULT_SETTINGS = {
    'site': {
        'name': 'My Great Site',
        'header_links': {},
        'language': 'en',
        'subtitle': None,
        'search_enabled': False,
        'author': None,
        'author_email': None,
        'url': None,
    },
}


EMPTY_CONFIG = '''
[site]
; Name of the site
name = {name}

; Language code
language = {language}

; A list of links to display in the header.
; header_links =
;     - /about/ about me
;     - /blog/ my blog
;     - /hobbies/ my hobbies
'''.rstrip()


def ask_for_value(question, default=None):
    """
    Ask the user for some input.

    :param question: Question to ask.
    :param allow_empty: If True, the user can enter nothing and still be
        accepted.  Otherwise, the user will keep being prompted until they
        enter a value.
    """
    if default is not None:
        question = '%s [%s]' % (question, default)
    while True:
        result = input(question + ' ')
        if result.strip():
            return result.strip()
        elif default is not None:
            return default


def create_new_settings():
    """
    Ask the user for their settings, and return the contents of a new
    settings file.
    """
    name = ask_for_value(
        'What is the name of the site?'
    )
    language = ask_for_value(
        'What language is the site written in?', default='en'
    )

    return EMPTY_CONFIG.format(
        name=name, language=language,
    )


class SiteSettings:

    def __init__(self, path):
        self.config = ConfigParser()
        self.config.read(os.path.join(path, 'config.ini'))

    def get(self, section, option):
        try:
            value = self.config.get(section, option)
        except (NoOptionError, NoSectionError):
            try:
                value = DEFAULT_SETTINGS[section][option]
            except KeyError:
                raise RuntimeError('No such setting %s:%s' % (section, option))

        if (section, option) == ('site', 'header_links'):
            result = collections.OrderedDict()
            for line in value.strip().splitlines():
                url, description = line.strip('-').strip().split(' ', 1)
                result[url] = description
            value = result

        return value
