#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import glob
import io
import os
import sys
from shutil import rmtree

from setuptools import Command, Extension, setup
from setuptools.command.test import test as TestCommand

import versioneer

# Package meta-data.
NAME = 'nanolib'
DESCRIPTION = \
    'Python library for working with the NANO cryptocurrency protocol'
URL = 'https://github.com/Matoking/nanolib'
EMAIL = 'jannepulk@gmail.com'
AUTHOR = 'Janne Pulkkinen'
REQUIRES_PYTHON = '>=3.6.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'bitarray>=0.8.1', 'ed25519-blake2b>=1.4', 'py-cpuinfo>=4'
]

NANOCURRENCY_WORK_REF = Extension(
    "nanolib._work_ref",
    include_dirs=[
        "src/nanolib-work-module/ref",
    ],
    sources=[
        "src/nanolib-work-module/work.c",
    ] + glob.glob("src/nanolib-work-module/ref/*.c"),
    extra_compile_args=["-DWORK_REF"]
)

NANOCURRENCY_WORK_SSE2 = Extension(
    "nanolib._work_sse2",
    include_dirs=[
        "src/nanolib-work-module/sse",
    ],
    sources=[
        "src/nanolib-work-module/work.c",
    ] + glob.glob("src/nanolib-work-module/sse/*.c"),
    extra_compile_args=["-DWORK_SSE2", "-msse2"]
)

NANOCURRENCY_WORK_SSSE3 = Extension(
    "nanolib._work_ssse3",
    include_dirs=[
        "src/nanolib-work-module/sse",
    ],
    sources=[
        "src/nanolib-work-module/work.c",
    ] + glob.glob("src/nanolib-work-module/sse/*.c"),
    extra_compile_args=["-DWORK_SSSE3", "-mssse3"]
)

NANOCURRENCY_WORK_SSE4_1 = Extension(
    "nanolib._work_sse4_1",
    include_dirs=[
        "src/nanolib-work-module/sse",
    ],
    sources=[
        "src/nanolib-work-module/work.c",
    ] + glob.glob("src/nanolib-work-module/sse/*.c"),
    extra_compile_args=["-DWORK_SSE4_1", "-msse4.1"]
)

NANOCURRENCY_WORK_AVX = Extension(
    "nanolib._work_avx",
    include_dirs=[
        "src/nanolib-work-module/sse",
    ],
    sources=[
        "src/nanolib-work-module/work.c",
    ] + glob.glob("src/nanolib-work-module/sse/*.c"),
    extra_compile_args=["-DWORK_AVX", "-mavx"]
)

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import shlex
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class SpeedTest(Command):
    description = (
        "Run a set of speed tests to measure performance of cryptographic "
        "operations"
    )
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from tests.performance_test import run_speed_tests

        run_speed_tests()


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(versioneer.get_version()))
        os.system('git push --tags')

        sys.exit()


cmdclass = versioneer.get_cmdclass()
cmdclass.update({
    'upload': UploadCommand,
    'speed': SpeedTest,
    'pytest': PyTest,
})

# Where the magic happens:
setup(
    name=NAME,
    version=versioneer.get_version(),
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    ext_modules=[
        NANOCURRENCY_WORK_REF,
        NANOCURRENCY_WORK_SSE2,
        NANOCURRENCY_WORK_SSSE3,
        NANOCURRENCY_WORK_SSE4_1,
        NANOCURRENCY_WORK_AVX,
    ],
    packages=["nanolib"],
    package_data={"": ["LICENSE"]},
    package_dir={"nanolib": "src/nanolib"},
    install_requires=REQUIRED,
    setup_requires=["sphinx"],
    tests_require=["pytest"],
    include_package_data=True,
    license='CC0',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        #  'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: POSIX :: Linux',
        'Topic :: Office/Business :: Financial',
    ],
    # $ setup.py publish support.
    cmdclass=cmdclass,
    command_options={
        'build_sphinx': {
            'project': ('setup.py', NAME),
            'version': ('setup.py', versioneer.get_version()),
            'source_dir': ('setup.py', 'docs')
        },
    }
)
