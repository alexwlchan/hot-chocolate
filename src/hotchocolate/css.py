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
import scss.compiler

# TODO: Make this a setting
STYLE_DIR = 'styles'


def optimize_css(css):
    """Given a CSS string, optimize and minify it as much as possible."""
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
        return subprocess.check_output(
            ['cleancss', '-O', '2', path]).decode('utf8')
    except (OSError, subprocess.CalledProcessError):
        return css
    finally:
        os.unlink(path)


class _InMemoryProcessor(mp.Processor):
    """A wrapper for doing in-memory stripping of unused CSS rules."""
    # The internals of this class are a bit messy and don't present themselves
    # well to doing in-memory operations: they expect to go out to the
    # filesystem and read files.  We have to change a few internal pieces
    # as we already have the file to hand.

    def download(self, url):
        return url

    def find_covering_css(self, body_html, css):
        self.process(f'<style>{css}</style><body>{body_html}</body>')
        try:
            return self.inlines[0].after
        except IndexError:
            return ''


def minimal_css_for_html(body_html, css):
    """Returns the minimal CSS required to render a block of body HTML."""
    proc = _InMemoryProcessor()
    return proc.find_covering_css(body_html=body_html, css=css)


def load_base_css(style_dir=None):
    """
    Load the ``style.scss`` file from the site's ``style`` directory, and
    return the base CSS for the site.
    """
    if style_dir is None:
        style_dir = STYLE_DIR

    return scss.compiler.compile_file(os.path.join(style_dir, 'style.scss'))
