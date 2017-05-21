# -*- encoding: utf-8

import os

from markdown import Extension
from markdown.preprocessors import Preprocessor
import pytest


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
