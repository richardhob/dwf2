#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from codecs import open
import os

PATH_HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(PATH_HERE, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dwf2',
    version='0.3.0',
    description="Digilent DWF library wrapper",
    long_description=long_description,
    url='https://github.com/richardhob/dwf2',
    author='Richard Hoberecht',
    author_email='richardhob@gmail.com',
    license='MIT',
    install_requires=[
        'enum34'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    platforms="Linux,Mac,Windows",
    packages=['dwf'],
    use_2to3=False
)
