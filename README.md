# statuspage

Status page application.

![django-statuspage preview](preview.png)


## Installation

Install the package

```sh
pip install https://github.com/edigiacomo/django-statuspage/archive/master.zip
```

Add the following applications to your Django projects

```python
INSTALLED_APPS += [
    'django.contrib.humanize',
    'rest_framework',
    'statuspage',
]
```

Update your urlconf:

```python
# myproject/urls.py
urlpatterns = [
    ...
    url(r'^statuspage/$', include('statuspage.urls', namespace='statuspage')),
]
```

Update your database

```sh
./manage migrate statuspage
```

## Usage

Service status can be managed from Django admin interface or using the REST
API.
