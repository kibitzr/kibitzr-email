#!/usr/bin/env python
from setuptools import setup


with open('requirements/base.in') as fp:
    install_requires = list(fp)


setup(
    name='kibitzr_email',
    version='1.0.0',
    description="Email fetcher for Kibitzr",
    long_description="TBD",
    author="Peter Demin",
    author_email='kibitzrrr@email.com',
    url='https://github.com/kibitzr/kibitzr-email',
    packages=[
        'kibitzr_email',
    ],
    package_dir={
        'kibitzr_email': 'kibitzr_email',
    },
    entry_points={
        'kibitzr.fetcher': [
            'fetcher=kibitzr_email:EmailPromoter',
        ],
        'kibitzr.cli': [
            'cli=kibitzr_email.cli:bind_commands',
        ],
    },
    include_package_data=True,
    install_requires=install_requires,
    license="MIT license",
    zip_safe=False,
    keywords='kibitzr email extension',
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
