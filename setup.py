#!/usr/bin/env python

import json
import sys
import urllib2

from setuptools import find_packages
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import call


def with_post_install(command):
    '''Runs the code in `modified_run` as a post-install step.'''
    original_run = command.run

    def modified_run(self):
        original_run(self)

        try:
            data = urllib2.urlopen('https://pypi.python.org/pypi/pytz/json').read()
            data = json.loads(data)
        except Exception:
            print 'Could not fetch latest pytz version! Falling back to default'
        else:
            latest_version = data['info']['version']
            releases = data['releases'][latest_version]

            release_url = None

            for release in releases:
                if release['url'].endswith('.zip'):
                    release_url = release['url']

            if hasattr(self, 'install_libbase'):
                dir_ = self.install_libbase  # setup.py install
            elif hasattr(self, 'install_dir'):
                dir_ = self.install_dir  # setup.py develop

            call_args = [sys.executable, 'build.py', 'all', '--dir', dir_]

            if release_url:
                call_args.extend(['--release-url', release_url])

            self.execute(lambda dir: call(call_args), (self.install_lib,), msg='Running post install task...')

    command.run = modified_run

    return command


@with_post_install
class Install(install):
    pass


@with_post_install
class Develop(develop):
    pass


setup(
    name='pytz-appengine',
    packages=find_packages(),
    cmdclass={
        'install': Install,
        'develop': Develop,
    },
)
