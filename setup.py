import os
import re

from setuptools import find_packages, setup


setup(
    name="django-statusboard",
    packages=find_packages(include=["statusboard", "statusboard.*"]),
    include_package_data=True,
    license='GPLv2+',
    description='Django app to show system status',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/edigiacomo/django-statusboard',
    author='Emanuele Di Giacomo',
    author_email="emanuele@digiacomo.cc",
    python_requires=">=3.6",
    install_requires=[
        'django>=2.2', 'djangorestframework', 'django-model-utils', 'pytz'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
