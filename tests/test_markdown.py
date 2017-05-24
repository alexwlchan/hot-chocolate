# -*- encoding: utf-8
"""
Tests for hotchocolate.markdown.
"""

import pytest

from hotchocolate import markdown


@pytest.mark.parametrize('source, expected', [
    # Basic examples
    (
        'Hello world',
        '<p>Hello world</p>'
    ),
    (
        'This is some *important* text',
        '<p>This is some <em>important</em> text</p>'
    ),
    (
        'An example with one paragraph.\n\nAnd a second paragraph.',
        '<p>An example with one paragraph.</p> <p>And a second paragraph.</p>'
    ),

    # Examples with footnotes
    (
        'A paragraph about a puffin[^1]\n\n[^1]: A footnote about Frankenstein',
        '<p>A paragraph about a puffin<sup id=fnref:2-1><a class=footnote-ref href=#fn:2-1 rel=footnote>1</a></sup></p> '
        '<div class=footnote> '
        '<hr> '
        '<ol> '
        '<li id=fn:2-1> '
        '<p>A footnote about Frankenstein&#160;<a class=footnote-backref href=#fnref:2-1 rev=footnote title="Jump back to footnote 1 in the text">&#8617;&#xFE0E;</a></p> '
        '</li> '
        '</ol> '
        '</div>'
    ),
    (
        'First with a flamingo[^1]\n\nSecond with a seagull[^2]\n\n'
        '[^1]: Footnote the First\n[^2]: Footnote the Second',
        '<p>First with a flamingo<sup id=fnref:2-1><a class=footnote-ref href=#fn:2-1 rel=footnote>1</a></sup></p> '
        '<p>Second with a seagull<sup id=fnref:2-2><a class=footnote-ref href=#fn:2-2 rel=footnote>2</a></sup></p> '
        '<div class=footnote> '
        '<hr> '
        '<ol> '
        '<li id=fn:2-1> '
        '<p>Footnote the First&#160;<a class=footnote-backref href=#fnref:2-1 rev=footnote title="Jump back to footnote 1 in the text">&#8617;&#xFE0E;</a></p> '
        '</li> '
        '<li id=fn:2-2> '
        '<p>Footnote the Second&#160;<a class=footnote-backref href=#fnref:2-2 rev=footnote title="Jump back to footnote 2 in the text">&#8617;&#xFE0E;</a></p> '
        '</li> '
        '</ol> '
        '</div>'
    ),

    # And with some code blocks
    (
        'A snippet of shell\n\n```bash\necho "hello world"\n```',
        '<p>A snippet of shell</p> '
        '<div class=codehilite><pre><span></span><span class=nb>echo</span> <span class=s2>&quot;hello world&quot;</span>\n'
        '</pre></div>'
    ),
])
def test_markdown_conversion(source, expected):
    assert markdown.convert_markdown(source)[0] == expected


def test_footnote_renders_with_text_marker():
    result = markdown.convert_markdown('Hello world[^1]\n\n[^1]: A footnote')
    assert '&#xFE0E' in result[0]


def test_renders_with_custom_extensions(md_extension):
    result = markdown.convert_markdown(
        'First phrase\nSecond stanza\nLast line',
        extra_extensions=[md_extension]
    )
    assert result[0] == '<p>test test test test test</p>'
