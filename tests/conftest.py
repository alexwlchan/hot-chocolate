# -*- encoding: utf-8

import os

from markdown import Extension
from markdown.preprocessors import Preprocessor
import pytest

from hotchocolate import Post


class EmptyPreprocessor(Preprocessor):
    """
    A preprocessor for testing purposes that replaces every line with
    the word 'test'.
    """
    def run(self, lines):
        return ['test'] * len(lines)


class EmptyExtension(Extension):
    """
    An extension for testing purposes that replaces every line with
    the word 'test'.
    """
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add(
            'dummy_extension',
            EmptyPreprocessor(md),
            '>normalize_whitespace')


@pytest.fixture
def md_extension():
    return EmptyExtension()


@pytest.fixture
def test_root():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def settings_dict():
    """Returns a complete set of site settings."""
    return {
        'name': 'Jane Doe',
        'url': 'https://example.org',
        'author': 'Jane Doe',
        'author_email': 'jane.doe@example.org',
        'description': 'An example website',
        'language': 'en',
    }


@pytest.fixture
def example_post():
    return Post(
        path='/dev/null',
        content='A post about greeting the entire globe',
        metadata={
            'date': '2016-07-21',
            'title': 'Hello world'
        }
    )
