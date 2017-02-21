from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.test import override_settings
from django.contrib.auth.models import User, Permission
from django.utils import timezone

from rest_framework.test import APIClient

from statusboard.models import Service
from statusboard.models import ServiceGroup
from statusboard.models import Incident


class TestApiPermission(TestCase):
    def setUp(self):
        self.anon_client = APIClient()

        createuser = User.objects.create_user(username="create")
        createuser.user_permissions.add(Permission.objects.get(codename="add_servicegroup"))
        createuser.save()
        self.create_client = APIClient()
        self.create_client.force_authenticate(createuser)

        deleteuser = User.objects.create_user(username="delete")
        deleteuser.user_permissions.add(Permission.objects.get(codename="delete_servicegroup"))
        deleteuser.save()
        self.delete_client = APIClient()
        self.delete_client.force_authenticate(deleteuser)

        edituser = User.objects.create_user(username="edit")
        edituser.user_permissions.add(Permission.objects.get(codename="change_servicegroup"))
        edituser.save()
        self.edit_client = APIClient()
        self.edit_client.force_authenticate(edituser)

    def test_servicegroup(self):
        """Test service group API permissions"""
        response = self.anon_client.get("/statusboard/api/v0.1/servicegroups/")
        self.assertEquals(response.status_code, 200)
        response = self.anon_client.post("/statusboard/api/v0.1/servicegroups/")
        self.assertEquals(response.status_code, 403)

        response = self.create_client.post("/statusboard/api/v0.1/servicegroups/", {
            "name": "test",
        })
        self.assertEquals(response.status_code, 201)
        self.assertTrue(ServiceGroup.objects.get(name="test") is not None)

        response = self.delete_client.patch("/statusboard/api/v0.1/servicegroups/1/", {
            "name": "t",
        })
        self.assertEquals(response.status_code, 403)
        self.assertTrue(ServiceGroup.objects.get(name="test") is not None)

        response = self.edit_client.patch("/statusboard/api/v0.1/servicegroups/1/", {
            "name": "t",
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(ServiceGroup.objects.get(name="t") is not None)


        response = self.create_client.delete("/statusboard/api/v0.1/servicegroups/1/")
        self.assertEquals(response.status_code, 403)
        self.assertEquals(ServiceGroup.objects.filter(pk=1).count(), 1)

        response = self.delete_client.delete("/statusboard/api/v0.1/servicegroups/1/")
        self.assertEquals(response.status_code, 204)
        self.assertEquals(ServiceGroup.objects.filter(pk=1).count(), 0)


@override_settings(MIDDLEWARE_CLASSES=[
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
], STATIC_URL='/static/')
class TestTemplate(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(username="admin",
                                              password="admin",
                                              email="admin@admin")
        admin.save()


    def test_service_create(self):
        client = Client()
        client.login(username="admin", password="admin")
        response = client.get('/statusboard/services/create/')
        self.assertEquals(response.status_code, 200)
        templates = [t.name for t in response.templates]
        self.assertTrue('statusboard/base.html' in templates)
        self.assertTrue('statusboard/service/create.html' in templates)
        self.assertTrue('statusboard/service/form.html' in templates)

    def test_maintenance_create(self):
        client = Client()
        client.login(username="admin", password="admin")
        response = client.get('/statusboard/maintenances/create/')
        self.assertEquals(response.status_code, 200)
        templates = [t.name for t in response.templates]
        self.assertTrue('statusboard/base.html' in templates)
        self.assertTrue('statusboard/maintenance/create.html' in templates)
        self.assertTrue('statusboard/maintenance/form.html' in templates)


@override_settings(MIDDLEWARE_CLASSES=[
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
], STATIC_URL='/static/')
class IncidentEdit(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(username="admin",
                                              password="admin",
                                              email="admin@admin")
        admin.save()

        s = Service(name="service", description="test", status=2)
        s.full_clean()
        s.save()
        i = Incident(name="incident", service=s)
        i.full_clean()
        i.save()

    def test_edit(self):
        client = Client()
        client.login(username="admin", password="admin")
        response = client.post('/statusboard/incidents/1/edit/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'service': 1,
            'service_status': 0,
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        s = Incident.objects.get(pk=1).service
        self.assertEquals(s.status, 0)

    def test_valid_status(self):
        client = Client()
        client.login(username="admin", password="admin")
        response = client.post('/statusboard/incidents/1/edit/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'service': 1,
            'service_status': 33,
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        s = Incident.objects.get(pk=1).service
        self.assertEquals(s.status, 2)


class TestIncidentManager(TestCase):
    def test_occurred_in_last_n_days(self):
        """Test for django 1.8 compatibility"""
        dt = timezone.datetime.now()
        days = 3
        s = Service.objects.create(name="service", description="test", status=0)
        Incident.objects.create(name="a", service=s, occurred=dt)
        Incident.objects.create(name="a", service=s, occurred=dt - timezone.timedelta(days=days))
        self.assertTrue(Incident.objects.occurred_in_last_n_days(days-1).count(), 1)
        self.assertTrue(Incident.objects.occurred_in_last_n_days(days).count(), 2)


class TestTemplateTags(TestCase):
    def test_servicegroup_collapse(self):
        g = ServiceGroup.objects.create(name="test", collapse=0)
        self.assertFalse(g.collapsed())

        g.collapse = 1
        g.save()
        self.assertTrue(g.collapsed())

        g.collapse = 2
        g.save()
        self.assertTrue(g.collapsed())

        s = Service.objects.create(name="service", description="test", status=0)
        s.groups = [g]
        s.save()
        g.collapse = 2
        g.save()
        self.assertTrue(g.collapsed())

        s.status = 1
        s.save()
        self.assertFalse(g.collapsed())


class TestService(TestCase):
    def test_worst_status(self):
        # ServiceManager
        self.assertEquals(Service.objects.worst_status(), None)
        # ServiceQuerySet
        self.assertEquals(Service.objects.all().worst_status(), None)


class TestServiceGroup(TestCase):
    def test_worst_service(self):
        g = ServiceGroup.objects.create(name="test", collapse=0)
        self.assertRaises(Service.DoesNotExist, g.worst_service)
        s = Service.objects.create(name="s0", description="test", status=0)
        g.services.add(s)
        g.save()
        self.assertEquals(g.worst_service(), s)
        s = Service.objects.create(name="s1", description="test", status=1)
        g.services.add(s)
        g.save()
        self.assertEquals(g.worst_service(), s)


class TestSettings(TestCase):
    def test_default(self):
        from statusboard.settings import conf
        self.assertIsNotNone(getattr(conf, "INCIDENT_DAYS_IN_INDEX"))
        self.assertTrue(hasattr(conf, "INCIDENT_DAYS_IN_INDEX"))
