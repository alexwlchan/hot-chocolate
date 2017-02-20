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

import os
import re
import warnings

import csscompressor
import mincss.processor as mp
import requests
import scss


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
        warnings.warn('Unable to minify CSS with CodeBeautifier: %s' % exc)
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
        # This step removes any CSS selectors that aren't used in the
        # provided HTML
        self.inlines = []
        self.process(html_str.replace(
            '<!-- hc_css_include -->', '<style>%s</style>' % css_str
        ))
        css_str = self.inlines[0].after

        # Now minify the CSS
        css_str = csscompressor.compress(css_str)

        # Finally, substitute the final CSS string and return the HTML
        return html_str.replace(
            '<!-- hc_css_include -->', '<style>%s</style>' % css_str
        )


class CSSProcessor:
    """
    Entry point for the CSS generator.
    """
    def __init__(self, path):
        self.base_css = self.get_base_css(path)
        self.minifier = CSSMinimiser()

    def insert_css_for_page(self, html_str):
        """
        Given the HTML contents of a page, fill in the minimal set of CSS
        required to render the page.
        """
        return self.minifier.render_html(html_str, self.base_css)

    def get_base_css(self, path):
        """
        Get the base site CSS, based on SCSS files in the package theme
        and anything in the ``style`` directory.
        """
        scss_compiler = scss.Compiler(search_path=[
            os.path.join('style'),
            os.path.join(os.path.dirname(__file__), 'style')
        ])

        # First we get the theme from the package itself.  This is kept
        # in ``style/main.scss`` within the package directory.
        # TODO: Is the `style` directory included in the package manifest?
        scss_str = open(
            os.path.join(os.path.dirname(__file__), 'style', 'main.scss')
        ).read()

        # Next look for ``style/custom.css`` in the site directory, and
        # try to add that.  If it doesn't exist, use the base theme.
        try:
            custom_scss = open(
                os.path.join(path, 'style', 'custom.scss')
            ).read()
            scss_str = custom_scss + scss_str + custom_scss
        except FileNotFoundError:
            pass

        css_str = scss_compiler.compile_string(scss_str)

        # Loading the custom theme may have introduced redundant selectors
        # (or heck, just carelessness from the person who wrote the CSS).
        # Consolidate selectors so we don't have redundant styles.
        css_str = _get_consolidated_css(css_str)

        return css_str
