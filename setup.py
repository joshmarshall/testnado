#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages


with open("VERSION") as version_fp:
    VERSION = version_fp.read().strip()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
INSTALL_REQUIRES = ["tornado>=4"]

if sys.version_info[0] == 2:
    INSTALL_REQUIRES.append("mock")

setup(
    name="testnado",
    version=VERSION,
    description="Tornado test helpers and Selenium testing with Tornado",
    author='Josh Marshall',
    author_email='catchjosh@gmail.com',
    url="http://github.com/joshmarshall/testnado/",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    packages=find_packages(where=PROJECT_ROOT, exclude=["tests", "dist"]),
    install_requires=INSTALL_REQUIRES
)
