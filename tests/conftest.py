# -*- encoding: utf-8

import os

from hotchocolate import Site
import hotchocolate.cli as hcli


# TODO: Tidy this up, and don't duplicate code from cli.py
curdir = os.path.abspath(os.curdir)
os.chdir('tests/examplesite')
site = Site.from_folder('content')
site.build()
os.chdir(curdir)
