#!/usr/bin/env python

from distutils.core import setup

setup(
    name="testnado",
    version="0.1",
    description="Tornado test helpers and Selenium testing with Tornado",
    author='Josh Marshall',
    author_email='catchjosh@gmail.com',
    url="http://github.com/joshmarshall/testnado/",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    packages=["testnado", "testnado.credentials"],
    install_requires=["tornado", "selenium", "mock", "nose"]
)
