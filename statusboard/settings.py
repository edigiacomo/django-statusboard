from django.conf import settings


"""
The settings for the app can be set in the project settings, e.g.:

    STATUSBOARD = {
        "INCIDENT_DAYS_IN_INDEX": 20,
    }
"""


DEFAULTS = {
    "INCIDENT_DAYS_IN_INDEX": 7,
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
