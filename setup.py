import os

from setuptools import find_packages, setup


def get_version(package):
    # Thanks to Tom Christie
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('statuspage')


setup(
    name="django-statuspage",
    version=version,
    packages=['statuspage'],
    include_package_data=True,
    license='GPLv2+',
    description='Django app to show system status',
    url='http://github.com/edigiacomo/django-statuspage',
    author='Emanuele Di Giacomo',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
