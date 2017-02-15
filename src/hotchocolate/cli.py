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
    site.build()


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
@click.option('--port', default=9000, help='port for the web server',
              type=click.IntRange(1024, 65535))
def serve(port):
    """
    Start a local web server for the site.
    """
    site = Site.from_folder('content')
    site.build()
    out_path = os.path.abspath(site.out_path)

    if not shutil.which('docker'):
        sys.exit('Unable to find Docker; please ensure Docker is installed '
                 'and in the PATH.')

    cmd = [
        # Run the container in the background
        'docker', 'run', '--detach',

        # Share the container port with the host
        '--publish', '%d:80' % port,

        # Share the output directory into the container
        '--volume', '%s:/usr/local/apache2/htdocs' % out_path,

        # Use the Apache container
        'httpd'
    ]
    try:
        subprocess.check_call(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        sys.exit('Error starting the container - is a container already '
                 'running on this port?')

    print('Web server running on http://localhost:%d/' % port)


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
    site.build()
