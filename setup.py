#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import os

from setuptools import find_packages, setup


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


SOURCE = local_file('src')
README = local_file('README.rst')
long_description = codecs.open(README, encoding='utf-8').read()


setup(
    name='hotchocolate',
    version='3.0.1',
    description='A static site generator designed for lightweight sites',
    long_description=long_description,
    url='https://github.com/alexwlchan/hot-chocolate',
    author='Alex Chan',
    author_email='alex@alexwlchan.net',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=find_packages(SOURCE),
    package_dir={'': SOURCE},
    include_package_data=True,
    install_requires=[
        'beautifulsoup4>=4.6.0,<5',
        'click>=6.7,<7',
        'csscompressor>=0.9.4,<1',
        'docker>=2.0.2,<3',
        'feedgenerator>=1.9,<2',
        'htmlmin>=0.1.10,<0.2',
        'python-dateutil>=2.6.0,<3',
        'Jinja2>=2.9.5,<3',
        'Markdown>=2.6.8,<3',
        'mincss>=0.11.2,<0.12',
        'Pygments>=2.2.0,<3',
        'pyScss>=1.3.5,<2',
        'toml>=0.9.2,<1',
        'unidecode>=0.04.20,<0.05',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'cocoa=hotchocolate.cli:cli',
        ],
    },
)
