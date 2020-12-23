#    Prana RC
#    Copyright (C) 2020 Dmitry Berezovsky
#    
#    prana is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    prana is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import fnmatch
import os
from os import path

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as build_py_orig

src_dir = path.abspath(path.dirname(__file__))
root_dir = path.join(src_dir, '..')

# == Read version ==
version_override = os.environ.get('VERSION_OVERRIDE', None) or None


def read_file(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read_file(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


if not version_override:
    version = get_version("prana_rc/__version__.py")
else:
    print("Using overridden version: " + version_override)
    version = version_override

# == END: Read version ==

# Get the long description from the README file
readme_file = path.join(root_dir, 'media/pypi-client-description.md')
try:
    from m2r import parse_from_file

    long_description = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()

included = [
    'prana_rc/__init__.py',
    'prana_rc/__version__.py',
    'prana_rc/entity.py',
    'prana_rc/utils.py',
    'prana_rc/contrib/__init__.py',
    'prana_rc/contrib/client/*.py',
    'prana_rc/contrib/api/*.py'
]


class build_py(build_py_orig):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [
            (pkg, mod, file)
            for (pkg, mod, file) in modules
            if any(fnmatch.fnmatchcase(file, pat=pattern) for pattern in included)
        ]


setup(
    name='prana_rc.client',
    # Semantic versioning should be used:
    # https://packaging.python.org/distributing/?highlight=entry_points#semantic-versioning-preferred
    version=version,
    description='Python library and CLI to control Prana recuperators via BLE connection (https://prana.org.ua/)',
    long_description=long_description,
    url='https://github.com/corvis/prana_rc',
    keywords='python prana recuperators iot automation',

    # Author
    author='Dmitry Berezovsky',

    # License
    license='GPLv3',

    # Technical meta
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Home Automation',

        # License (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Python versions support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>3.6',

    # Structure
    packages=find_packages(include=['prana_rc', 'prana_rc.*']),

    install_requires=[
        'ws-sizzle[aiohttp]>=0.0.8'
    ],

    # Extra dependencies might be installed with:
    # pip install -e .[dev,test]
    extras_require={
    },

    package_data={
        # 'examples': [path.join(root_dir, 'examples')],
    },
    cmdclass={'build_py': build_py},

    script_name='client_setup.py'
)
