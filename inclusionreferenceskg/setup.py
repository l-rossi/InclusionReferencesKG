#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Lukas Rossi",
    author_email='l.rossi@tum.de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Inclusion of Reference Information in EU Regulations using Knowledge Graphs",
    entry_points={
        'console_scripts': [
            'inclusionreferenceskg=inclusionreferenceskg.cli:src',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='inclusionreferenceskg',
    name='inclusionreferenceskg',
    packages=find_packages(include=['inclusionreferenceskg', 'inclusionreferenceskg.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ge93xax/inclusionreferenceskg',
    version='0.1.0',
    zip_safe=False,
)
