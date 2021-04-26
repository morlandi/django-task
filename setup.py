#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from setuptools import find_packages, setup


def get_version(*file_paths):
    """Retrieves the version from django_task/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("django_task", "__init__.py")
readme = open('README.rst').read()
history = open('CHANGELOG.rst').read().replace('.. :changelog:', '')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-task',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A Django app to run new background tasks from either admin or cron, and inspect task history from admin; based on django-rq',
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    author='Mario Orlandi',
    author_email='morlandi@brainstorm.it',
    url='https://github.com/morlandi/django-task',
    zip_safe=False,
    keywords='django-task',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
)
