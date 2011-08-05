# -*- coding: utf-8 -*-

"""
    gletools
    ~~~~~~~~

    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
    
from setuptools import setup

setup(
    name                    = 'gletools',
    version                 = '0.1.0', 
    description             = 'Advanced opengl utilities for pyglet',
    long_description        = __doc__,
    license                 = 'GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) Version 3',
    url                     = 'http://hg.codeflow.org/gletools',
    download_url            = 'http://hg.codeflow.org/',
    author                  = 'Florian Boesch',
    author_email            = 'pyalot@gmail.com',
    maintainer              = 'Florian Boesch',
    maintainer_email        = 'pyalot@gmail.com',
    zip_safe                = True,
    include_package_data    = True,
    packages                = ['gletools'],
    install_requires        = ['setuptools', 'pyglet'],
    platforms               = ['any'],
)
