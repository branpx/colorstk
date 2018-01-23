#!/usr/bin/env python

from setuptools import setup

setup(
    name='colorstk',
    author='Brandon Piatt',
    author_email='branpx@gmail.com',
    url='http://github.com/branpx/colorstk',
    license='MIT',
    packages=['colorstk'],
    package_data={'colorstk': ['data/*', '*.kv']},
    exclude_package_data={'colorstk': ['data/svg/*']},
    install_requires=['kivy', 'grapefruit'],
    dependency_links=['git+http://github.com/xav/grapefruit.git'],
    entry_points={'gui_scripts': ['colorstk=colorstk.main:main']}
    )
