# -*- encoding: utf-8

import os
import shutil
import subprocess
import sys

import click
import docker
import requests

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

    # Set up the Docker API
    client = docker.from_env()

    # Check that Docker is available
    try:
        client.info()
    except requests.exceptions.ConnectionError:
        sys.exit('Unable to connect to Docker.')

    #
    try:
        client.containers.run(
            image='httpd',
            detach=True,
            ports={port: 80},
            read_only=True,
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
