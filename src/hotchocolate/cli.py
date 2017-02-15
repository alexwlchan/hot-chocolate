# -*- encoding: utf-8

import os
import shutil
import subprocess
import sys

import click

from . import Site


@click.group()
def cli():
    pass


@cli.command('build', help='(re)build the HTML for the website')
def build():
    """
    Take the content folder and build it.
    """
    site = Site.from_folder('content')
    site.build('output')


@cli.command('clean', help='remove the generated HTML')
def clean():
    """
    Delete the output folder, if it exists.
    """
    try:
        shutil.rmtree('output')
    except FileNotFoundError:
        pass


@cli.command('serve', help='serve the generated website on a local port')
def serve():
    """
    Start a server on port 8900.
    """
    site = Site.from_folder('content')
    site.build('output')

    os.chdir('output')
    if shutil.which('docker'):
        # TODO: Don't error if the container is already running
        # TODO: Let the user choose what port to use
        subprocess.check_call(
            ['docker', 'run', '-d', '-p', '8900:80',
             '-v', '%s:/usr/local/apache2/htdocs' % os.path.abspath(os.curdir),
             'httpd'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        # TODO: Add support for a server with http.server
        print('Running the local web server requires Docker')
        sys.exit(1)
    print('Web server runnning on http://localhost:8900/')


@cli.command('publish', help='build the HTML for publication')
def publish():
    """
    The ``build`` command won't clean up pages or links that no longer exist.
    This command builds a fresh copy of the site, free of dead links.
    """
    for f in os.listdir('output'):
        path = os.path.join('output', f)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

    site = Site.from_folder('content')
    site.build('output')
