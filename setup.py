#!/usr/bin/env python

from setuptools import setup, find_packages


with open("VERSION") as version_fp:
    VERSION = version_fp.read().strip()

setup(
    name="testnado",
    version=VERSION,
    description="Tornado test helpers and Selenium testing with Tornado",
    author='Josh Marshall',
    author_email='catchjosh@gmail.com',
    url="http://github.com/joshmarshall/testnado/",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    packages=find_packages(exclude=["tests", "dist"]),
    install_requires=["tornado", "selenium", "mock"]
)
