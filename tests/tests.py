from django.test import TestCase
from django.contrib.auth.models import User, Permission

from rest_framework.test import APIClient

from statusboard.models import ServiceGroup


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
