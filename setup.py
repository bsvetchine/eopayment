#!/usr/bin/env python

'''
Setup script for eopayment
'''

import distutils
import distutils.core
from glob import glob
from os.path import splitext, basename, join as pjoin
import os
from unittest import TextTestRunner, TestLoader

class TestCommand(distutils.core.Command):
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''
        testfiles = [ ]
        for t in glob(pjoin(self._dir, 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['tests', splitext(basename(t))[0]])
                )

        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 4)
        t.run(tests)

def get_version():
    import glob
    import re
    import os

    version = None
    for d in glob.glob('*'):
        if not os.path.isdir(d):
            continue
        module_file = os.path.join(d, '__init__.py')
        if not os.path.exists(module_file):
            continue
        for v in re.findall("""__version__ *= *['"](.*)['"]""",
                open(module_file).read()):
            assert version is None
            version = v
        if version:
            break
    assert version is not None
    if os.path.exists('.git'):
        import subprocess
        p = subprocess.Popen(['git','describe','--dirty','--match=v*'],
                stdout=subprocess.PIPE)
        result = p.communicate()[0]
        assert p.returncode == 0, 'git returned non-zero'
        new_version = result.split()[0][1:]
        assert not new_version.endswith('-dirty'), 'git workdir is not clean'
        assert new_version.split('-')[0] == version, '__version__ must match the last git annotated tag'
        version = new_version.replace('-', '.')
    return version

distutils.core.setup(name='eopayment',
        version=get_version(),
        license='GPLv3 or later',
        description='Common API to use all French online payment credit card processing services',
        long_description=
            "eopayment is a Python module to interface with French's bank credit card\n"
            "online payment services. Supported services are ATOS/SIP, SystemPay, and\n"
            "SPPLUS.",
        url='http://dev.entrouvert.org/projects/eopayment/',
        author="Entr'ouvert",
        author_email="info@entrouvert.com",
        maintainer="Benjamin Dauvergne",
        maintainer_email="bdauvergne@entrouvert.com",
        packages=['eopayment', 'tests'],
        requires=[
            'pycrypto (>= 2.5)'
        ],
        cmdclass={'test': TestCommand})
