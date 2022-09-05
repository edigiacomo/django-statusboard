# Copyright (C) 2017 Emanuele Di Giacomo <emanuele@digiacomo.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.templatetags.static import static


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
    "FAVICON_DEFAULT": static(
        "statusboard/favicons/statusboard-icon-default.ico"
    ),
    # Favicons for index
    "FAVICON_INDEX_DICT": {
        0: static("statusboard/favicons/statusboard-icon-operational.ico"),
        1: static("statusboard/favicons/statusboard-icon-performance.ico"),
        2: static("statusboard/favicons/statusboard-icon-partial.ico"),
        3: static("statusboard/favicons/statusboard-icon-major.ico"),
    },
}


class Settings(object):
    """Settings for internal use."""

    def __getattr__(self, name):
        if name not in DEFAULTS:
            raise RuntimeError(
                ("{} is not a valid statusboard " "setting").format(name)
            )
        s = getattr(settings, "STATUSBOARD", {})
        return s.get(name, DEFAULTS[name])


statusconf = Settings()
