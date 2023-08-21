import json
import random

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from utils.constants import REGISTRATION_EMAIL
from utils.factories import VendorFactory, SuperUserFactory, CustomerUserFactory, AttachmentFactory, MailFactory


class MailViewSetTest(APITestCase):
    def setUp(self):
        self.vendor = VendorFactory()
        self.superuser = SuperUserFactory()
        self.customer_user = CustomerUserFactory()
        self.mails = []
        for _ in range(10):
            self.mails.append(MailFactory())

    def test_create_mail(self):
        self.client.force_authenticate(user=self.superuser)
        attachment = AttachmentFactory()
        data = {
            "type": REGISTRATION_EMAIL,
            "title": "Test Email",
            "order_num": "123",
            "template": "email_template",
            "text": "This is a test mail",
            "to_email": "test@example.com",
            "bcc": "bcc@example.com",
            "cc": "cc@example.com",
            "from_email": "postmaster@kintyazilim.com",
            "from_user": "testuser",
            "attachments": [attachment.id],
            "is_active": True,
            "vendor": self.vendor.id,
            "customer": self.customer_user.id,
            "created_by": self.superuser.id
        }

        response = self.client.post(reverse('mail-list'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_mail(self):
        self.client.force_authenticate(user=self.superuser)
        mail = self.mails[random.randint(0, len(self.mails) - 1)]
        response = self.client.get(reverse('mail-detail', kwargs={'pk': mail.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], mail.id)

    def test_update_mail(self):
        self.client.force_authenticate(user=self.superuser)
        mail = self.mails[random.randint(0, len(self.mails) - 1)]
        original_title = mail.title
        new_title = "Updated Title"
        data = {"title": new_title}

        response = self.client.put(reverse('mail-detail', kwargs={'pk': mail.id}),
                                   data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotEqual(original_title, response.data['title'])

    def test_delete_mail(self):
        self.client.force_authenticate(user=self.superuser)
        mail = self.mails[random.randint(0, len(self.mails) - 1)]
        response = self.client.delete(reverse('mail-detail', kwargs={'pk': mail.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
