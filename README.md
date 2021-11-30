# statusboard

[![Build Status](https://github.com/edigiacomo/django-statusboard/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/edigiacomo/django-statusboard/actions/workflows/build.yml)
[![Pypi](https://img.shields.io/pypi/v/django-statusboard.svg)](https://pypi.python.org/pypi/django-statusboard/)
[![codecov](https://codecov.io/gh/edigiacomo/django-statusboard/branch/main/graph/badge.svg)](https://codecov.io/gh/edigiacomo/django-statusboard)
[![Documentation Status](https://readthedocs.org/projects/django-statusboard/badge/?version=stable)](https://django-statusboard.readthedocs.io/en/stable/?badge=stable)

Status page application with browser and REST API interface.

## Installation

Install the package

```sh
pip install django-statusboard
```

Add the following applications to your Django projects

```python
INSTALLED_APPS += [
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'rest_framework',
    'statusboard',
]
```

Update your urlconf:

```python
# myproject/urls.py
urlpatterns += [
    url(r'^statusboard/$', include('statusboard.urls')),
]
```

Update your database

```sh
./manage migrate
```

## Configuration

You can configure the app using the dict `STATUSBOARD` in `settings.py`:

```python
from django.contrib.staticfiles.templatetags.staticfiles import static
# for Django >= 3.0: from django.templatetags.static import static

STATUSBOARD = {
    "INCIDENT_DAYS_IN_INDEX": 7,
    "OPEN_INCIDENT_IN_INDEX": True,
    "AUTO_REFRESH_INDEX_SECONDS": 0,
    "FAVICON_DEFAULT": static('statusboard/images/statusboard-icon-default.png'),
    "FAVICON_INDEX_DICT": {
        0: static('statusboard/images/statusboard-icon-operational.png'),
        1: static('statusboard/images/statusboard-icon-performance.png'),
        2: static('statusboard/images/statusboard-icon-partial.png'),
        3: static('statusboard/images/statusboard-icon-major.png'),
    },
}
```

* `INCIDENT_DAYS_IN_INDEX`: number of days to show in index (1 = today).
* `OPEN_INCIDENT_IN_INDEX`: show not fixed incidents in index, whether or not
  the incident is older than `INCIDENT_DAYS_IN_INDEX`.
* `AUTO_REFRESH_INDEX_SECONDS`: auto refresh home page every N seconds (0 = disabled).
* `FAVICON_DEFAULT`: default favicon.
* `FAVICON_INDEX_DICT`: favicon for index, based on the worst status (default:
  `FAVICON_DEFAULT`). The keys `(0, 1, 2, 3)` are the status values (see `SERVICE_STATUSES` in `statusboard/models.py`).

## Customize pages

The following blocks are customizable in `statusboard/base.html`:

* `title`: title of the page
* `branding`: branding in fixed navbar
* `bootstrap_theme`: bootstrap theme
* `header`: header of the page
* `userlinks`: links in the header
* `footer`: footer div
* `style`: `CSS` files
* `script`: JavaScript files

To customize the default style, create the file `statusboard/base.html` that
extends the original base template and customize some blocks, e.g.:

```
{% extends "statusboard/base.html" %}

{% load static %}

{% block title %}
A.C.M.E. statuspage
{% endblock %}

{% block branding %}
<a class="navbar-brand" href="{% url 'statusboard:index' %}"><img src="{% static "/images/logo.png" %}"></a>
{% endblock %}

{% block bootstrap_theme %}
<link rel="stylesheet" href="{% static "/statusboard/css/spacelab-bootstrap.min.css" %}" />
<link rel="stylesheet" href="{% static "/css/mystyle.css" %}" />
{% endblock %}
```

### Example: change branding and title

In Django >= 1.9, the templates can be extended recursively (see
https://docs.djangoproject.com/en/1.9/releases/1.9/#templates).

Create a `statusboard/base.html` in one of your templates dir:

```
{% extends `statusboard/base.html %}

{% block title %}
ACME, Inc.
{% endblock %}

{% block branding %}
<a class="navbar-brand" href="{% url 'statusboard:index' %}">ACME status</a>
{% endblock %}
```

## Notifications

`django-statusboard` doesn't provide an out-of-the-box notification system, but
it's easy to implement using [django signals](https://docs.djangoproject.com/en/dev/topics/signals/).

Moreover, `django-statusboard` tracks the previous status of a service
(`Service._status`).

```python
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import mail_admins

from statusboard import Service

@receiver(post_save, sender=Service)
def notify_service_update(sender, instance, **kwargs):
    # Send an email to admins if the service is getting worse, otherwise do nothing.
    if instance.status > instance._status:
        mail_admins("Alert", "Service {} is {}".format(instance.name, instance.get_status_display()))
```

## REST API

`django-statusboard` comes with a set of REST API to manage its models, based on [Django REST Framework](https://www.django-rest-framework.org/) `ModelViewSet`.


## Development

### Running tests

```
$ DJANGO_SETTINGS_MODULE=tests.test_settings python manage.py test
```

### Update i18n

```
$ cd statusboard && django-admin makemessages -l LOCALE
```



## Contact and copyright information

Copyright (C) 2019 Emanuele Di Giacomo <emanuele@digiacomo.cc>

django-statusboard is licensed under GPLv2+.
