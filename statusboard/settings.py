from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static


"""
The settings for the app can be set in the project settings, e.g.:

    STATUSBOARD = {
        "INCIDENT_DAYS_IN_INDEX": 20,
    }
"""


DEFAULTS = {
    # Number of incidents in index (1 = today, 0 = deactivate)
    "INCIDENT_DAYS_IN_INDEX": 7,
    # Show or not all the open incidents in index
    "OPEN_INCIDENT_IN_INDEX": True,
    # Automatic refresth the home page in seconds (disable with 0)
    "AUTO_REFRESH_INDEX_SECONDS": 0,
    # Default favicon
    "FAVICON_DEFAULT": static('statusboard/favicons/statusboard-icon-default.ico'),
    # Favicons for index
    "FAVICON_INDEX_DICT": {
        0: static('statusboard/favicons/statusboard-icon-operational.ico'),
        1: static('statusboard/favicons/statusboard-icon-performance.ico'),
        2: static('statusboard/favicons/statusboard-icon-partial.ico'),
        3: static('statusboard/favicons/statusboard-icon-major.ico'),
    }
}


class Settings(object):
    """Settings for internal use."""
    def __getattr__(self, name):
        if name not in DEFAULTS:
            raise RuntimeError(("{} is not a valid statusboard "
                                "setting").format(name))
        s = getattr(settings, "STATUSBOARD", {})
        return s.get(name, DEFAULTS[name])


statusconf = Settings()
