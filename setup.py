#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="numcrunch-academy",
    version="1.0",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    package_data={
        'game': ['assets/*', 'assets/**/*'],
    },
    include_package_data=True,
    install_requires=['pygame>=2.0'],
    entry_points={
        'console_scripts': ['numcrunch=game.NumCrunch_Academy:main']
    }
)
