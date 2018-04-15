#!/usr/bin/env python
from setuptools import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()


setup(
    name='kibitzr_keyring',
    version='0.0.1',
    description="Keyring support for Kibitzr",
    long_description=readme,
    author="Peter Demin",
    author_email='kibitzrrr@gmail.com',
    url='https://github.com/kibitzr/kibitzr-keyring',
    py_modules=['kibitzr_keyring'],
    entry_points={
        'kibitzr.creds': [
            'keyring=kibitzr_keyring:KeyringCreds',
        ]
    },
    include_package_data=True,
    install_requires=[
        'keyring',
    ],
    license="MIT license",
    zip_safe=False,
    keywords='kibitzr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-pep8',
        'pylint',
        'mock',
        'pytest-mock',
    ],
)
