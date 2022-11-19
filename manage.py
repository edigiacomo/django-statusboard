import os

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
import django
from django.core.management import execute_from_command_line


if __name__ == "__main__":
    django.setup()
    execute_from_command_line()
