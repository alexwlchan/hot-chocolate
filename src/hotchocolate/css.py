# -*- encoding: utf-8
"""
Implements the CSS processors.

Because static site generators do all their processing upfront, you can
spend time in the build step optimising the CSS for the smallest size.
Remove duplicate selectors, optimise layout, minify, etc.

Hot Chocolate goes one step further -- it's designed for sites with a very
small CSS footprint (single-digit KB), so it puts the CSS in a <style> tag
within the <head> of the page -- after reducing it to only the selectors
required to render the current page.  This means that every page loads the
smallest amount of CSS it can get away with.

"""

import os
import subprocess
import tempfile

import csscompressor
import mincss.processor as mp
import scss


def cleancss(css):
    """
    Run the CSS through the cleancss Node tool
    (https://github.com/jakubpawlowicz/clean-css).

    If the tool is unavailable, it just returns the CSS string unmodified.
    """
    # To run cleancss, the CSS must be in a file.
    _, path = tempfile.mkstemp()
    with open(path, 'w') as fp:
        fp.write(css)

    try:
        return subprocess.check_output(['cleancss', '-O', '2', path])
    except (OSError, subprocess.CalledProcessError):
        return css
    finally:
        os.unlink(path)


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
        css_str = cleancss(css_str)

        return css_str

    def insert_css_for_page(self, html_str):
        """
        Given the HTML contents of a page, fill in the minimal set of CSS
        required to render the page.
        """
        return CSSMinimiser().render_html(html_str, self.base_css)
