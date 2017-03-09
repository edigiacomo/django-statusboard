# statusboard

[![Build Status](https://travis-ci.org/edigiacomo/django-statusboard.svg?branch=master)](https://travis-ci.org/edigiacomo/django-statusboard)
[![Pypi](https://img.shields.io/pypi/v/django-statusboard.svg)](https://pypi.python.org/pypi/django-statusboard/)

Status page application.

## Installation

Install the package

```sh
pip install django-statusboard
```

Add the following applications to your Django projects

```python
INSTALLED_APPS += [
    'django.contrib.humanize',
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
STATUSBOARD = {
    "INCIDENT_DAYS_IN_INDEX": 7,
    "OPEN_INCIDENT_IN_INDEX": True,
}
```

* `INCIDENT_DAYS_IN_INDEX`: number of days to show in index (1 = today).
* `OPEN_INCIDENT_IN_INDEX`: show not fixed incidents in index.

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

### Example: change branding and title


#### Django 1.8

Copy `statusboard/templates/statusboard/base.html` in one of your templates dir
and edit the file.

#### Django >= 1.9

In Django >= 1.9, the templates can be extended recursively (see
https://docs.djangoproject.com/en/1.10/releases/1.9/).

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
    mail_admins("Alert",
                "Service {} is {}".format(instance.name, instance.get_status_display()))
```
