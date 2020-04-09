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

from os import path
from setuptools import setup, find_packages
import prana_rc.__version__

src_dir = path.abspath(path.dirname(__file__))
root_dir = path.join(src_dir, '..')

version = prana_rc.__version__.__version__

# Get the long description from the README file
readme_file = path.join(root_dir, 'README.md')
try:
    from m2r import parse_from_file

    long_description = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()

setup(
    name='prana_rc',
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
        'Topic :: Software Development :: Build Tools',

        # License (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Python versions support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # Structure
    packages=find_packages(include=['prana_rc', 'prana_rc.*']),
    # py_modules=["app", 'cli', 'daemonize'],

    install_requires=[
        'bleak>=0.6.1',
        'typing>=3.6',
        'service_identity>=18.0.0',
    ],

    # Extra dependencies might be installed with:
    # pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': [],
    },

    package_data={
        # 'examples': [path.join(root_dir, 'examples')],
    },

    # test_suite='nose2.collector.collector',
    # tests_require=[
    #     'nose2==0.8.0',
    # ],
    entry_points={
        'console_scripts': [
            'prana=prana_rc.cli:main',
        ],
    }
)