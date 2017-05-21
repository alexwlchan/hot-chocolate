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


def optimize(css):
    """
    Given a CSS string, optimize and minify it as much as possible.
    """
    # Run it through the cleancss tool
    css = cleancss(css)

    # Minify it, stripping out comments and whitespace.  This is arguably
    # redundant because cleancss can do this for us, but it's a good fallback
    # if cleancss fails for some reason.
    css = csscompressor.compress(css)

    return css


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


class _InMemoryProcessor(mp.Processor):
    """
    A wrapper for doing in-memory stripping of unused CSS rules.
    """
    # The internals of this class are a bit messy and don't present themselves
    # well to doing in-memory operations: they expect to go out to the
    # filesystem and read files.  We have to change a few internal pieces
    # as we already have the file to hand.

    def download(self, url):
        return url

    def render_html(self, body_html, css):
        self.process(f'<style>{css}</style><body>{body_html}</body>')
        return self.inlines[0].after


def minimal_css_for_html(body_html, css):
    """
    Returns the minimal CSS required to render a block of body HTML.
    """
    proc = _InMemoryProcessor()
    return proc.render_html(body_html=body_html, css=css)


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
        self.base_css = optimize(self.get_base_css(path))

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
        return self.scss_compiler.compile_string(self.base_scss)

    def insert_css_for_page(self, html_str):
        """
        Given the HTML contents of a page, fill in the minimal set of CSS
        required to render the page.
        """
        css = minimal_css_for_html(
            html_str=html_str.split('<body>')[1].split('</body>')[0],
            css=self.base_css
        )
        return html_str.replace(
            '<!-- hc_css_include -->', f'<style>{css}</style>')
