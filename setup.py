# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='v2c',
    version='0.1.0',
    description='Create container image from running Linux machine',
    long_description=readme,
    author='Kazuhiro Takahashi',
    author_email='hidakanoko.k7@gmail.com',
    url='https://github.com/hidakanoko/vm2container',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)