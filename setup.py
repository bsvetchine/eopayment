#!/usr/bin/env python

'''
Setup script for eopayment
'''

import subprocess
import distutils
import distutils.core
import setuptools
from distutils.command.sdist import sdist
from glob import glob
from os.path import splitext, basename, join as pjoin, dirname
import os
from unittest import TextTestRunner, TestLoader
import doctest


class TestCommand(distutils.core.Command):
    user_options = []

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''
        testfiles = []
        for t in glob(pjoin(self._dir, 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['tests', splitext(basename(t))[0]])
                )

        tests = TestLoader().loadTestsFromNames(testfiles)
        import eopayment
        tests.addTests(doctest.DocTestSuite(eopayment))
        t = TextTestRunner(verbosity=4)
        t.run(tests)


class eo_sdist(sdist):

    def run(self):
        print ("creating VERSION file")
        if os.path.exists('VERSION'):
            os.remove('VERSION')
        version = get_version()
        version_file = open('VERSION', 'w')
        version_file.write(version)
        version_file.close()
        sdist.run(self)
        print ("removing VERSION file")
        if os.path.exists('VERSION'):
            os.remove('VERSION')


def get_version():
    '''Use the VERSION, if absent generates a version with git describe, if not
       tag exists, take 0.0.0- and add the length of the commit log.
    '''
    if os.path.exists('VERSION'):
        with open('VERSION', 'r') as v:
            return v.read()
    if os.path.exists('.git'):
        p = subprocess.Popen(['git', 'describe', '--dirty',
                              '--match=v*'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        result = p.communicate()[0]
        if p.returncode == 0:
            version = result.split()[0][1:]
            version = version.replace('-', '.')
            return version
    return '0.0.0'

setuptools.setup(
    name='eopayment',
    version=get_version(),
    license='GPLv3 or later',
    description='Common API to use all French online payment credit card '
    'processing services',
    long_description=open(
        os.path.join(
            os.path.dirname(__file__),
            'README.txt')).read(),
    url='http://dev.entrouvert.org/projects/eopayment/',
    author="Entr'ouvert",
    author_email="info@entrouvert.com",
    maintainer="Benjamin Dauvergne",
    maintainer_email="bdauvergne@entrouvert.com",
    packages=['eopayment'],
    install_requires=[
        'pycrypto >= 2.5'
    ],
)
