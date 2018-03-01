#!/usr/bin/env python

from os.path import dirname, join
import re
from subprocess import check_call

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


def _post_install():
        try:
            import kivy.garden.iconfonts
        except KeyError:
            check_call(['garden', 'install', 'iconfonts'])


class PostDevelop(develop):
    def run(self):
        _post_install()
        develop.run(self)


class PostInstall(install):
    def run(self):
        _post_install()
        install.run(self)


version_file = join(dirname(__file__), 'colorstk', '__init__.py')
with open(version_file) as vfile:
    lines = vfile.readlines()
for line in lines:
    line = line.strip()
    if line.startswith('__version__ = '):
        matches = re.findall(r'["\']([^"\']*)["\']', line)
        if matches:
            version = matches[0]
            break
        else:
            raise RuntimeError(
                'Could not load version from {}'.format(version_file))

setup(
    name='colorstk',
    version=version,
    description='Kivy app featuring color conversions and other tools',
    author='Brandon Piatt',
    author_email='branpx@gmail.com',
    url='http://github.com/branpx/colorstk',
    license='MIT',
    packages=['colorstk'],
    package_data={'colorstk': ['data/*', '*.kv']},
    exclude_package_data={'colorstk': ['data/svg/*']},
    install_requires=['kivy', 'kivy-garden', 'grapefruit'],
    dependency_links=['git+http://github.com/xav/grapefruit.git'],
    entry_points={'gui_scripts': ['colorstk=colorstk.main:main']},
    cmdclass={'develop': PostDevelop, 'install': PostInstall}
    )
