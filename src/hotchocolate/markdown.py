# -*- encoding: utf-8
"""
Implements the Markdown parser.

This module exports a single function, which converts Markdown source into
HTML, and then returns the HTML.  It doesn't do any I/O -- everything is just
pure in-memory strings.
"""

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.meta import MetaExtension
from markdown.extensions.smarty import SmartyExtension


def convert_markdown(source, extra_extensions=None, parse_metadata=True):
    """
    Convert a Markdown string into HTML.  Returns an (HTML, metadata) tuple.

    This renders vanilla Markdown, and also footnotes, fenced code blocks
    and syntax-highlighting for code blocks.  Additional extensions can
    be supplied in the ``extra_extensions`` parameter.

    :param source: Markdown source.
    :param extra_extensions: (optional) A list of Extensions to use.
    :param parse_metadata: (optional) Should we parse metadata in the string?

    """
    # Rather than load all the extensions every time, we load only the
    # extensions required for the given source.  Informal testing in the old
    # implementation suggested this made a difference.
    # TODO: Is this still required?
    extensions = [SmartyExtension()]

    if parse_metadata:
        extensions.append(MetaExtension())

    # Look for evidence of footnotes.
    if '[^' in source:
        fn_extension = FootnoteExtension(
            # We may show multiple documents with footnotes on an index
            # page.  Ensure footnote references are globally unique.
            # TODO: Make footnote numbering consistent over multiple
            # builds even when the set of pages/posts changes.
            UNIQUE_IDS=True,

            # Make sure that footnote markers are rendered as a text
            # arrow on iOS devices, not emoji.  For more info:
            # http://daringfireball.net/linked/2015/04/22/unicode-emoji
            BACKLINK_TEXT='&#8617;&#xFE0E;',
        )
        extensions.append(fn_extension)

    if '```' in source:
        extensions.extend([
            CodeHiliteExtension(),
            FencedCodeExtension(),
        ])

    if extra_extensions is not None:
        extensions.extend(extra_extensions)

    md = markdown.Markdown(extensions=extensions)
    html = md.convert(source)

    if parse_metadata:
        return (html, md.Meta)
    else:
        return html
