import sys

if __name__ == "__main__":
    import django
    from django.core.management import execute_from_command_line
    django.setup()
    execute_from_command_line(sys.argv)
