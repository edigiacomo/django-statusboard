import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def runtests(test_labels=["tests"]):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(test_labels)
    sys.exit(bool(failures))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("test_label", nargs="*", default=["tests"])
    args = parser.parse_args()
    runtests(args.test_label)
