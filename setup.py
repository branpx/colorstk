#!/usr/bin/env python

from setuptools import setup

setup(
    name='colorstk',
    author='Brandon Piatt',
    author_email='branpx@gmail.com',
    url='http://github.com/branpx/colorstk',
    license='MIT',
    packages=['colorstk'],
    package_data={'colorstk': ['*.kv']},
    install_requires=['grapefruit'],
    dependency_links=['git+http://github.com/xav/grapefruit.git'],
    entry_points={'gui_scripts': ['colorstk=colorstk.main:main']}
    )
