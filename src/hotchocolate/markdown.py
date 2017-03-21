# -*- encoding: utf-8

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.smarty import SmartyExtension

from .plugins import load_markdown_extensions


class Markdown(object):
    """
    A Cocoa-specific variant of ``markdown.Markdown``.

    This sets up the necessary extensions and reset points.
    """
    def __init__(self):
        self.custom_extensions = load_markdown_extensions()

    def convert(self, source):
        """
        Convert a Markdown source into HTML.
        """
        extensions = [
            SmartyExtension(),
        ]

        if '[^' in source:
            extensions.append(
                FootnoteExtension(configs={
                    # We may show multiple documents with footnotes on an index
                    # page.  Ensure footnote references are globally unique.
                    # TODO: Make footnote numbering consistent over multiple
                    # builds even when the set of pages/posts changes.
                    'UNIQUE_IDS': True,

                    # Make sure that footnote markers are rendered as a text
                    # arrow on iOS devices, not emoji.  For more info:
                    # http://daringfireball.net/linked/2015/04/22/unicode-emoji
                    'BACKLINK_TEXT': '&#8617;&#xFE0E;',
                })
            )

        if '```' in source:
            extensions.extend([
                CodeHiliteExtension(),
                FencedCodeExtension(),
            ])
        extensions.extend(self.custom_extensions)

        md = markdown.Markdown(extensions=extensions)
        return md.convert(source)
