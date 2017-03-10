# -*- encoding: utf-8

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.smarty import SmartyExtension

from .plugins import load_markdown_extensions


class Markdown(markdown.Markdown):
    """
    A Cocoa-specific variant of ``markdown.Markdown``.

    This sets up the necessary extensions and reset points.
    """
    def __init__(self):
        extensions = [
            CodeHiliteExtension(),
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
            }),
            FencedCodeExtension(),
            SmartyExtension(),
        ] + load_markdown_extensions()

        super().__init__(extensions=extensions)

    def convert(self, source, src_id=None):
        """
        Convert a Markdown source into HTML.
        """
        # Reset the footnote extension, so we don't have footnotes carrying
        # across multiple documents.
        for ext in self.registeredExtensions:
            if isinstance(ext, FootnoteExtension):
                ext.reset()
        return super().convert(source)
