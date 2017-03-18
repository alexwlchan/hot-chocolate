# -*- encoding: utf-8

import os
import shutil
import sys
import time

import click
import docker
import requests

from . import Site
from .logging import success
from .settings import create_new_settings


@click.group()
def cli():
    pass


@cli.command('build', help='(re)build the HTML for the website')
def build():
    """
    Take the content folder and build it.
    """
    start = time.time()
    site = Site.from_folder(os.curdir)
    site.build()
    success('Site build completed in %.2f seconds', time.time() - start)


@cli.command('clean', help='remove the generated HTML')
def clean():
    """
    Delete the output folder, if it exists.
    """
    # TODO: This will clobber the Docker container's volume mount, if present
    # Stop and delete the container if it's running.
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

    # Set up the Docker API
    client = docker.from_env()

    # Check that Docker is available
    try:
        client.info()
    except requests.exceptions.ConnectionError:
        sys.exit('Unable to connect to Docker.')

    # Start the container
    try:
        client.containers.run(
            image='httpd',
            detach=True,
            ports={80: port},
            volumes={
                os.path.abspath(site.out_path): {
                    'bind': '/usr/local/apache2/htdocs',
                    'mode': 'ro',
                },
            },
        )
    except docker.errors.APIError as err:
        sys.exit('Error starting the Docker container:\n%s' % err)

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


@cli.command('init', help='start a new Hot Chocolate site')
def init():
    """
    The ``init`` command creates a new site.
    """
    config_str = create_new_settings()
    with open('config.ini', 'w') as cfgfile:
        cfgfile.write(config_str)

    for dirname in ('pages', 'posts', 'static', 'style', 'templates'):
        os.makedirs(dirname, exist_ok=True)
