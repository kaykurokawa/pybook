#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pybook',
      version='0.1',
      description='Order book written in python',
      author='Umpei Kay Kurokawa',
      packages=['pybook'],
      )

