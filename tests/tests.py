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


class TestServiceGroup(TestCase):
    def test_position_order(self):
        s0 = ServiceGroup.objects.create(name="s0", position=1)
        s1 = ServiceGroup.objects.create(name="s1", position=0)
        self.assertEquals(ServiceGroup.objects.all()[0], s0)
        self.assertEquals(ServiceGroup.objects.all()[1], s1)
        self.assertEquals(ServiceGroup.objects.position_sorted()[0], s1)
        self.assertEquals(ServiceGroup.objects.position_sorted()[1], s0)
        # When two groups have the same position, order by name
        s2 = ServiceGroup.objects.create(name="s2", position=0)
        self.assertEquals(ServiceGroup.objects.position_sorted()[0], s1)
        self.assertEquals(ServiceGroup.objects.position_sorted()[1], s2)
        self.assertEquals(ServiceGroup.objects.position_sorted()[2], s0)
