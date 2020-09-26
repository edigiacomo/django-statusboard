import os
import re

from setuptools import find_packages, setup



def get_version(package):
    # Thanks to Tom Christie
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def read_md(path):
    try:
        import pypandoc
        return pypandoc.convert(path, 'rst')
    except ImportError:
        return open(path).read()


version = get_version('statusboard')

setup(
    name="django-statusboard",
    version=version,
    packages=find_packages(include=["statusboard", "statusboard.*"]),
    include_package_data=True,
    license='GPLv2+',
    description='Django app to show system status',
    long_description=read_md('README.md'),
    url='http://github.com/edigiacomo/django-statusboard',
    author='Emanuele Di Giacomo',
    author_email="emanuele@digiacomo.cc",
    python_requires=">=3.5",
    install_requires=[
        'django>=2.2', 'djangorestframework', 'django-model-utils', 'pytz'
    ],
    test_suite="runtests.runtests",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
