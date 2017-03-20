# -*- encoding: utf-8
"""
This file contains the CSS pipeline for Hot Chocolate.

CSS is an area where static site generation can make a big performance win.
There's a threshhold around 12KB where it becomes more efficient to
inline your CSS than make a second TCP request -- but at the cost of no
caching.  H/C is intended for sites with very small CSS files -- often less
than half the 12KB threshhold -- so inlining makes a lot of sense.

Once you have inlining in each page, you can use the compile step to make
it as efficient as possible:

*   Minify the CSS
*   Remove selectors that aren't used in the current page
*   Consolidate selectors to minimise the CSS size

"""

import html
import os
import re

import csscompressor
import mincss.processor as mp
import requests
import scss

from .logging import warning


def _get_consolidated_css(css_str):
    """
    Try to get a consolidated CSS string using http://www.codebeautifier.com/.

    If this fails it's not a disaster, we just might have slightly more
    inefficient CSS strings, so we only warn on exceptions.
    """
    try:
        r = requests.post(
            'http://www.codebeautifier.com/',
            data={'css_text': css_str}
        )
        encoded_css = r.text.split('<code id="code">')[1].split('</code>')[0]
        encoded_css = re.sub(r'<[^>]+>', r'', encoded_css)

        # If there were characters that get HTML encoded in the CSS, we
        # need to turn them back into literal characters.  For example:
        #
        #     a:before { content: "foo"; }
        #
        # becomes
        #
        #     a:before { content: &quot;foo&quot;; }
        #
        encoded_css = html.unescape(encoded_css)

        # There's an interesting bug with CodeBeautifier, possibly because
        # it runs to an old version of the CSS spec, where it mangles media
        # queries.  Specifically, this:
        #
        #     @media screen and (max-width: 500px) { a { color: red; } }
        #
        # becomes:
        #
        #     @media screen and max-width 500px { a { color: red; } }
        #
        # which no longer works.  Fix that up by hand: the media queries
        # used in Hot Chocolate sites should be fairly simple.
        #
        encoded_css = re.sub(
            r'@media screen and (max|min)-width ([0-9]+)px',
            r'@media screen and (\1-width: \2px)',
            encoded_css
        )

        return encoded_css
    except Exception as exc:
        warning('Unable to minify CSS with CodeBeautifier: %s' % exc)
        return css_str


class CSSMinimiser(mp.Processor):
    """
    A wrapper around ``mincss.Processor`` that's designed to do in-memory
    stripping of unused/duplicate CSS rules, minify the result and return
    the final HTML string.
    """
    def download(self, url):
        return url

    def render_html(self, html_str, css_str):
        self.process('<style>%s</style><body>%s</body>' % (
            css_str, html_str.split('<body>')[1].split('</body>')[0]))
        css_str = self.inlines[0].after

        # Finally, substitute the final CSS string and return the HTML
        return html_str.replace(
            '<!-- hc_css_include -->', '<style>%s</style>' % css_str
        )


class CSSProcessor:
    """
    Entry point for the CSS generator.
    """
    def __init__(self, path):
        # Minify the CSS so we don't have to deal with comments or whitespace
        self.scss_compiler = scss.Compiler(search_path=[
            os.path.join('style'),
            os.path.join(os.path.dirname(__file__), 'style')
        ])
        self.base_scss = self.get_base_scss(path)
        self.base_css = csscompressor.compress(self.get_base_css(path))

    def get_base_scss(self, path):
        """
        Get the base site SCSS.
        """
        # First we get the theme from the package itself.  This is kept
        # in ``style/main.scss`` within the package directory.
        # TODO: Is the `style` directory included in the package manifest?
        scss_str = open(
            os.path.join(os.path.dirname(__file__), 'style', 'main.scss')
        ).read()

        # Next look for ``style/variables.scss`` in the site directory, and
        # try to add that.  If it doesn't exist, use the base theme.
        try:
            variables_scss = open(
                os.path.join(path, 'style', 'variables.scss')
            ).read()
            scss_str = variables_scss + scss_str
        except FileNotFoundError:
            pass

        try:
            custom_scss = open(
                os.path.join(path, 'style', 'custom.scss')
            ).read()
            scss_str = scss_str + custom_scss
        except FileNotFoundError:
            pass

        return scss_str

    def get_base_css(self, path):
        """
        Get the base site CSS, based on SCSS files in the package theme
        and anything in the ``style`` directory.
        """
        css_str = self.scss_compiler.compile_string(self.base_scss)

        # Loading the custom theme may have introduced redundant selectors
        # (or heck, just carelessness from the person who wrote the CSS).
        # Consolidate selectors so we don't have redundant styles.
        css_str = _get_consolidated_css(css_str)

        return css_str

    def insert_css_for_page(self, html_str):
        """
        Given the HTML contents of a page, fill in the minimal set of CSS
        required to render the page.
        """
        return CSSMinimiser().render_html(html_str, self.base_css)
