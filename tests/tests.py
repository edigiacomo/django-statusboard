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

from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User, Permission
from django.utils import timezone

from rest_framework.test import APIClient

from statusboard.models import Service
from statusboard.models import ServiceGroup
from statusboard.models import Incident
from statusboard.models import IncidentUpdate
from statusboard.models import Maintenance


class TestApiPermission(TestCase):
    def setUp(self):
        self.anon_client = APIClient()

        createuser = User.objects.create_user(username="create")
        createuser.user_permissions.add(
            Permission.objects.get(codename="add_servicegroup")
        )
        createuser.save()
        self.create_client = APIClient()
        self.create_client.force_authenticate(createuser)

        deleteuser = User.objects.create_user(username="delete")
        deleteuser.user_permissions.add(
            Permission.objects.get(codename="delete_servicegroup")
        )
        deleteuser.save()
        self.delete_client = APIClient()
        self.delete_client.force_authenticate(deleteuser)

        edituser = User.objects.create_user(username="edit")
        edituser.user_permissions.add(Permission.objects.get(
            codename="change_servicegroup")
        )
        edituser.save()
        self.edit_client = APIClient()
        self.edit_client.force_authenticate(edituser)

    def test_servicegroup(self):
        """Test service group API permissions"""
        response = self.anon_client.get("/statusboard/api/v0.1/servicegroup/")
        self.assertEquals(response.status_code, 200)
        response = self.anon_client.post("/statusboard/api/v0.1/servicegroup/")
        self.assertEquals(response.status_code, 403)

        response = self.create_client.post(
            "/statusboard/api/v0.1/servicegroup/", {
                "name": "test",
            }
        )
        self.assertEquals(response.status_code, 201)
        self.assertTrue(ServiceGroup.objects.get(name="test") is not None)

        response = self.delete_client.patch(
            "/statusboard/api/v0.1/servicegroup/1/", {
                "name": "t",
            }
        )
        self.assertEquals(response.status_code, 403)
        self.assertTrue(ServiceGroup.objects.get(name="test") is not None)

        response = self.edit_client.patch(
            "/statusboard/api/v0.1/servicegroup/1/", {
                "name": "t",
            }
        )
        self.assertEquals(response.status_code, 200)
        self.assertTrue(ServiceGroup.objects.get(name="t") is not None)

        response = self.create_client.delete(
            "/statusboard/api/v0.1/servicegroup/1/"
        )
        self.assertEquals(response.status_code, 403)
        self.assertEquals(ServiceGroup.objects.filter(pk=1).count(), 1)

        response = self.delete_client.delete(
            "/statusboard/api/v0.1/servicegroup/1/"
        )
        self.assertEquals(response.status_code, 204)
        self.assertEquals(ServiceGroup.objects.filter(pk=1).count(), 0)


class TestTemplate(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(username="admin",
                                              password="admin",
                                              email="admin@admin")
        admin.save()

    def test_service_create(self):
        client = Client()
        client.login(username="admin", password="admin")
        response = client.get('/statusboard/service/create/')
        self.assertEquals(response.status_code, 200)
        templates = [t.name for t in response.templates]
        self.assertTrue('statusboard/base.html' in templates)
        self.assertTrue('statusboard/service/create.html' in templates)
        self.assertTrue('statusboard/service/form.html' in templates)

    def test_maintenance_create(self):
        client = Client()
        client.login(username="admin", password="admin")
        response = client.get('/statusboard/maintenance/create/')
        self.assertEquals(response.status_code, 200)
        templates = [t.name for t in response.templates]
        self.assertTrue('statusboard/base.html' in templates)
        self.assertTrue('statusboard/maintenance/create.html' in templates)
        self.assertTrue('statusboard/maintenance/form.html' in templates)

    def test_index_refresh(self):
        client = Client()

        # Default: no refresh
        response = client.get('/statusboard/')
        self.assertNotContains(response, text='<meta http-equiv="refresh"')

        with self.settings(STATUSBOARD={
            "AUTO_REFRESH_INDEX_SECONDS": 0
        }):
            response = client.get('/statusboard/')
            self.assertNotContains(response, text='<meta http-equiv="refresh"')

        with self.settings(STATUSBOARD={
            "AUTO_REFRESH_INDEX_SECONDS": 1
        }):
            response = client.get('/statusboard/')
            self.assertContains(response,
                                text='<meta http-equiv="refresh" content="1">')

    def test_index_favicon(self):
        from statusboard.settings import statusconf

        client = Client()
        # Test default favicons
        response = client.get('/statusboard/')
        self.assertContains(response, status_code=200,
                            text=statusconf.FAVICON_DEFAULT)

        s1 = Service.objects.create(name="s1", description="test", status=0)
        for status in (0, 1, 2, 3):
            s1.status = status
            s1.save()
            response = client.get('/statusboard/')
            self.assertContains(response, status_code=200,
                                text=statusconf.FAVICON_INDEX_DICT[status])

        # This service is always operational so it doesn't affect the icon
        # image
        Service.objects.create(name="s2", description="test", status=0)

        # Test custom favicons
        with self.settings(STATUSBOARD={
            'FAVICON_DEFAULT': 'default',
            'FAVICON_INDEX_DICT': {
                0: '0',
                1: '1',
                2: '2',
                3: '3',
            },
        }):
            for status in (0, 1, 2, 3):
                s1.status = status
                s1.save()
                response = client.get('/statusboard/')
                self.assertContains(response, status_code=200,
                                    text=statusconf.FAVICON_INDEX_DICT[status])

        # Test custom favicons (default only)
        with self.settings(STATUSBOARD={
            'FAVICON_DEFAULT': 'default',
            'FAVICON_INDEX_DICT': {}
        }):
            for status in (0, 1, 2, 3):
                s1.status = status
                s1.save()
                response = client.get('/statusboard/')
                self.assertContains(response, status_code=200,
                                    text=statusconf.FAVICON_DEFAULT)


class TestIncidentCreate(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(username="admin",
                                              password="admin",
                                              email="admin@admin")
        admin.save()

        Service.objects.create(name="s1", description="s1", status=2)
        Service.objects.create(name="s2", description="s2", status=2)

    def test_create(self):
        client = Client()
        client.login(username="admin", password="admin")
        client.post('/statusboard/incident/create/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'services': [1, 2],
            'service_status': 0,
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        incident = Incident.objects.get(pk=1)
        self.assertEquals(incident.services.count(), 2)
        for s in incident.services.all():
            self.assertEquals(s.status, 0)

    def test_create_without_services(self):
        client = Client()
        client.login(username="admin", password="admin")
        client.post('/statusboard/incident/create/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'services': [],
            'service_status': 0,
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        incident = Incident.objects.get(pk=1)
        self.assertEquals(incident.services.count(), 0)

    def test_create_with_empty_service_status(self):
        client = Client()
        client.login(username="admin", password="admin")
        client.post('/statusboard/incident/create/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'services': [1, 2],
            'service_status': '',
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        incident = Incident.objects.get(pk=1)
        self.assertEquals(incident.services.count(), 2)
        for s in incident.services.all():
            self.assertEquals(s.status, 2)


class TestIncidentEdit(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(username="admin",
                                              password="admin",
                                              email="admin@admin")
        admin.save()

        s1 = Service.objects.create(name="s1", description="s1", status=2)
        s2 = Service.objects.create(name="s2", description="s2", status=2)
        i = Incident(name="incident")
        i.full_clean()
        i.save()
        i.services.add(s1)
        i.services.add(s2)
        i.full_clean()
        i.save()

    def test_edit(self):
        client = Client()
        client.login(username="admin", password="admin")
        client.post('/statusboard/incident/1/edit/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'services': [1, 2],
            'service_status': 0,
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        incident = Incident.objects.get(pk=1)
        self.assertEquals(incident.services.count(), 2)
        for s in incident.services.all():
            self.assertEquals(s.status, 0)

    def test_edit_with_empty_service_status(self):
        client = Client()
        client.login(username="admin", password="admin")
        client.post('/statusboard/incident/1/edit/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'services': [1, 2],
            'service_status': '',
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        incident = Incident.objects.get(pk=1)
        self.assertEquals(incident.services.count(), 2)
        for s in incident.services.all():
            self.assertEquals(s.status, 2)

    def test_edit_remove_service(self):
        client = Client()
        client.login(username="admin", password="admin")
        client.post('/statusboard/incident/1/edit/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'services': 1,
            'service_status': 0,
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        i = Incident.objects.get(pk=1)
        self.assertEquals(i.services.count(), 1)

    def test_valid_status(self):
        client = Client()
        client.login(username="admin", password="admin")
        client.post('/statusboard/incident/1/edit/', {
            'name': 'incident',
            'occurred': '2010-01-01 00:00:00',
            'services': [1, 2],
            'service_status': 33,
            'updates-INITIAL_FORMS': 0,
            'updates-TOTAL_FORMS': 0,
            'updates-MAX_NUM_FORMS': 0,
            'updates-MIN_NUM_FORMS': 0,
        })
        i = Incident.objects.get(pk=1)
        s = i.services.first()
        self.assertEquals(s.status, 2)


class TestServiceGroup(TestCase):
    def test_priority_order(self):
        s0 = ServiceGroup.objects.create(name="s0", priority=1)
        s1 = ServiceGroup.objects.create(name="s1", priority=0)
        self.assertEquals(ServiceGroup.objects.all()[0], s0)
        self.assertEquals(ServiceGroup.objects.all()[1], s1)
        self.assertEquals(ServiceGroup.objects.priority_sorted()[0], s0)
        self.assertEquals(ServiceGroup.objects.priority_sorted()[1], s1)
        # When two groups have the same priority, order by name
        s2 = ServiceGroup.objects.create(name="s2", priority=0)
        self.assertEquals(ServiceGroup.objects.priority_sorted()[0], s0)
        self.assertEquals(ServiceGroup.objects.priority_sorted()[1], s1)
        self.assertEquals(ServiceGroup.objects.priority_sorted()[2], s2)
        # Filter queryset object
        self.assertEquals(
            ServiceGroup.objects.filter(name="s1").priority_sorted()[0], s1
        )

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

    def test_is_empty_group(self):
        g = ServiceGroup.objects.create(name="test", collapse=0)
        self.assertTrue(g.is_empty_group())
        s = Service.objects.create(name="s1", description="test", status=1)
        g.services.add(s)
        g.save()
        self.assertFalse(g.is_empty_group())


class TestIncidentManager(TestCase):
    def setUp(self):
        dt = timezone.datetime.now()
        days = 30
        i = Incident.objects.create(name="a", occurred=dt)
        IncidentUpdate.objects.create(incident=i, status=0, description="test")
        IncidentUpdate.objects.create(incident=i, status=3, description="test")
        i = Incident.objects.create(name="b",
                                    occurred=dt-timezone.timedelta(days=days))
        IncidentUpdate.objects.create(incident=i, status=0, description="test")
        self.days = days

    def test_occurred_in_last_n_days(self):
        self.assertEquals(
            Incident.objects.occurred_in_last_n_days(self.days-1).count(), 1
        )
        self.assertEquals(
            Incident.objects.occurred_in_last_n_days(self.days).count(), 1
        )

    def test_last_occurred(self):
        with self.settings(STATUSBOARD={
            "INCIDENT_DAYS_IN_INDEX": self.days+2,
        }):
            self.assertEquals(Incident.objects.last_occurred().count(), 2)

        with self.settings(STATUSBOARD={
            "INCIDENT_DAYS_IN_INDEX": self.days+1,
        }):
            self.assertEquals(Incident.objects.last_occurred().count(), 2)

        with self.settings(STATUSBOARD={
            "INCIDENT_DAYS_IN_INDEX": self.days,
        }):
            self.assertEquals(Incident.objects.last_occurred().count(), 1)

        with self.settings(STATUSBOARD={
            "INCIDENT_DAYS_IN_INDEX": self.days-1,
        }):
            self.assertEquals(Incident.objects.last_occurred().count(), 1)

        with self.settings(STATUSBOARD={
            "INCIDENT_DAYS_IN_INDEX": 1,
        }):
            self.assertEquals(Incident.objects.last_occurred().count(), 1)

        with self.settings(STATUSBOARD={
            "INCIDENT_DAYS_IN_INDEX": 0,
        }):
            self.assertEquals(Incident.objects.last_occurred().count(), 0)

    def test_in_index(self):
        self.assertEquals(Incident.objects.in_index().count(), 2)

        with self.settings(STATUSBOARD={
            "OPEN_INCIDENT_IN_INDEX": True,
            "INCIDENT_DAYS_IN_INDEX": self.days+1,
        }):
            self.assertEquals(Incident.objects.in_index().count(), 2)

        with self.settings(STATUSBOARD={
            "OPEN_INCIDENT_IN_INDEX": True,
            "INCIDENT_DAYS_IN_INDEX": 0,
        }):
            self.assertEquals(Incident.objects.in_index().count(), 1)

        with self.settings(STATUSBOARD={
            "OPEN_INCIDENT_IN_INDEX": False,
            "INCIDENT_DAYS_IN_INDEX": 0,
        }):
            self.assertEquals(Incident.objects.in_index().count(), 0)


class TestIncident(TestCase):
    def test_closed(self):
        i = Incident.objects.create(name="incident")
        self.assertFalse(i.closed)
        IncidentUpdate.objects.create(incident=i, status=0, description="test")
        self.assertFalse(i.closed)
        IncidentUpdate.objects.create(incident=i, status=3, description="test")
        self.assertTrue(i.closed)
        IncidentUpdate.objects.create(incident=i, status=0, description="test")
        self.assertFalse(i.closed)


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

        s = Service.objects.create(name="service", description="test",
                                   status=0)
        s.groups.add(g)
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

    def test_previous_status(self):
        from django.db.models.signals import post_save

        def check_different(sender, instance, **kwargs):
            check_different.is_different = (
                instance._status != instance.status
            )

        check_different.is_different = None

        post_save.connect(check_different)

        s = Service(name="service", description="test", status=0)
        s.save()
        self.assertFalse(check_different.is_different)
        s.status = 0
        s.save()
        self.assertFalse(check_different.is_different)
        s.status = 1
        s.save()
        self.assertIsNotNone(check_different.is_different)
        self.assertTrue(check_different.is_different)

        post_save.disconnect(check_different)


class TestSettings(TestCase):
    def test_default(self):
        from statusboard.settings import statusconf

        self.assertIsNotNone(getattr(statusconf, "INCIDENT_DAYS_IN_INDEX"))
        self.assertTrue(hasattr(statusconf, "INCIDENT_DAYS_IN_INDEX"))

    def test_modified(self):
        from django.conf import settings
        from statusboard.settings import statusconf

        with self.settings(STATUSBOARD={
            "INCIDENT_DAYS_IN_INDEX": 30,
        }):
            self.assertEquals(statusconf.INCIDENT_DAYS_IN_INDEX, 30)
            self.assertEquals(settings.STATUSBOARD["INCIDENT_DAYS_IN_INDEX"],
                              statusconf.INCIDENT_DAYS_IN_INDEX)

    def test_missing_default(self):
        from statusboard.settings import statusconf

        with self.assertRaises(RuntimeError):
            statusconf.THIS_IS_A_MISSING_APP_SETTING


class TestMaintenanceEdit(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(username="admin",
                                              password="admin",
                                              email="admin@admin")
        admin.save()

        m = Maintenance(scheduled=timezone.datetime.now(),
                        name="test",
                        description="test")
        m.full_clean()
        m.save()

    def test_edit(self):
        client = Client()
        client.login(username="admin", password="admin")
        dt = timezone.datetime.now()
        client.post('/statusboard/maintenance/1/edit/', {
            'scheduled': dt,
            'name': 'modified name',
            'description': 'modified description',
        })
        m = Maintenance.objects.get(pk=1)
        self.assertEquals(m.scheduled, dt)
        self.assertEquals(m.name, "modified name")
        self.assertEquals(m.description, "modified description")


class TestReverseAndResolve(TestCase):
    def test_maintenance(self):
        from django.urls import reverse, resolve

        self.assertEquals(
            reverse('statusboard:maintenance:create'),
            '/statusboard/maintenance/create/',
        )
        resolver = resolve('/statusboard/maintenance/create/')
        self.assertEquals(
            resolver.namespaces,
            ['statusboard', 'maintenance'],
        )
        self.assertEquals(
            resolver.view_name,
            'statusboard:maintenance:create',
        )


class TestPermissionRequiredView(TestCase):
    def test_permission_required(self):
        with self.settings(LOGIN_URL='/login'):
            client = Client()
            response = client.get('/statusboard/service/create/')
            self.assertRedirects(response,
                                 '/login?next=/statusboard/service/create/',
                                 fetch_redirect_response=False)


class TestChangePermission(TestCase):
    def setUp(self):
        edituser = User.objects.create_user(username="edit", password="edit")
        edituser.user_permissions.add(
            Permission.objects.get(codename="change_service")
        )
        edituser.save()
        self.client = Client()
        self.client.login(username='edit', password='edit')

        self.servicegroup = ServiceGroup.objects.create(name="g1")
        self.service = Service.objects.create(name="s1", description="s1",
                                              status=2)

    def test_change_service(self):
        self.client.post(
            '/statusboard/service/{}/edit/'.format(self.service.pk), {
                'name': 's1-changed',
                'description': self.service.description,
                'href': self.service.href,
                'status': self.service.status,
                'priority': self.service.priority,
                'groups': [self.servicegroup.pk],
            }
        )
        self.assertEquals(Service.objects.get(pk=self.service.pk).name,
                          's1-changed')


class TestArchiveIncident(TestCase):
    def test_archive_index_empty(self):
        from django.urls import reverse
        client = Client()
        resp = client.get(reverse('statusboard:incident:archive-index'))
        self.assertTrue('statusboard/incident/archive_month_empty.html' in [
            t.name for t in resp.templates
        ])

    def test_archive_index_nonempty(self):
        from django.urls import reverse
        i = Incident.objects.create(name="incident")
        client = Client()
        resp = client.get(reverse('statusboard:incident:archive-index'))
        self.assertRedirects(
            resp,
            reverse('statusboard:incident:archive-month', args=[
                i.created.year, i.created.month
            ])
        )
