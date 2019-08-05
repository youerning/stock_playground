# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import os
import sys
from codecs import open

from setuptools import setup
from setuptools.command.test import test as TestCommand


here = os.path.abspath(os.path.dirname(__file__))
packages = ['nobody']

requires = open(os.path.join(here, "requirement.txt")).readlines()

test_requirements = [
    'pytest>=2.8.0'
]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count
            self.pytest_args = ['-n', str(cpu_count()), '--boxed']
        except (ImportError, NotImplementedError):
            self.pytest_args = ['-n', '1', '--boxed']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


about = {}
with open(os.path.join(here, 'nobody', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)


setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    packages=packages,
    package_dir={'nobody': 'nobody'},
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=requires,
    license=about['__license__'],
    zip_safe=False,
    cmdclass={'test': PyTest},
    tests_require=test_requirements
)
