# -*- encoding: utf-8

import os
import tempfile

from jinja2 import (
    Environment, FileSystemLoader, PackageLoader, select_autoescape)


class CocoaEnvironment(object):
    """
    Wrapper for ``jinja2.Environment`` that allows the user to override
    templates with files in a local directory.
    """
    def __init__(self, path):
        self.workdir = tempfile.mkdtemp(prefix='cocoa_templates_')

        # Drop in any templates from the local directory.  Because we need
        # to cope with relative imports and the like, we just copy them
        # all to a temporary directory and work from there.
        try:
            for tmpl in os.listdir(os.path.join(path, 'templates')):
                if os.path.basename(tmpl).startswith('.'):
                    continue
                os.link(
                    src=os.path.abspath(tmpl),
                    dst=os.path.join(self.workdir, os.path.basename(tmpl))
                )

            if os.listdir(self.workdir) == []:
                raise FileNotFoundError('No custom templates')

        # If there aren't any custom templates, just use them directly
        # from the package itself.
        except FileNotFoundError:
            self.env = Environment(
                loader=PackageLoader('hotchocolate', 'templates'),
                autoescape=select_autoescape(['html'])
            )

        # Otherwise, copy across the templates from the package
        # directory and then use a FileSystemLoader.
        else:
            package_dir = os.path.join(os.path.dirname(__file__), 'templates')
            print(self.workdir)
            for tmpl in os.listdir(package_dir):
                name = os.path.basename(tmpl)
                if name.startswith('.'):
                    continue
                try:
                    os.link(
                        src=os.path.abspath(tmpl),
                        dst=os.path.join(self.workdir, name)
                    )
                except FileExistsError:
                    pass
            self.env = Environment(
                loader=FileSystemLoader(self.workdir),
                autoescape=select_autoescape(['html'])
            )

    def get_template(self, *args, **kwargs):
        return self.env.get_template(*args, **kwargs)


def write_html(output_dir, slug, string):
    """
    Writes a string to a path in the output directory.

    This creates a directory with an ``index.html`` file, so you get
    pretty URLs without needing web server configuration.
    """
    slug = slug.lstrip('/')
    os.makedirs(os.path.join(output_dir, slug), exist_ok=True)
    with open(os.path.join(output_dir, slug, 'index.html'), 'w') as f:
        f.write(string)