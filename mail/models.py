import logging
import os

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from mysite.settings import BASE_DIR
from user.models import User
from utils.constants import PASSWORD_RESET_EMAIL, REGISTRATION_EMAIL


class Mail(models.Model):
    class Meta:
        verbose_name_plural = 'Emails'
        verbose_name = 'Email'
        db_table = "email"
        ordering = ["-pk"]

    TYPES = (
        (REGISTRATION_EMAIL, "Registration Email"),
        (PASSWORD_RESET_EMAIL, "Password Reset Email"),
    )

    type = models.CharField(max_length=100, blank=True, null=True, choices=TYPES)
    title = models.CharField(max_length=255, blank=True, null=True)
    template = models.CharField(max_length=255, blank=True, null=True)

    text = models.TextField(max_length=25000, blank=True, null=True)
    to_email = models.CharField(max_length=500, blank=True, null=True)
    bcc = models.CharField(max_length=500, blank=True, null=True)
    cc = models.CharField(max_length=500, blank=True, null=True)
    from_email = models.CharField(max_length=500, blank=True, null=True)
    from_user = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    created_by = models.ForeignKey(User, blank=True, null=True, verbose_name="Created By",
                                   related_name="mail_created_by", on_delete=models.SET_NULL)
    deleted_by = models.ForeignKey(User, blank=True, null=True, verbose_name="Deleted By",
                                   related_name="mail_deleted_by", on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk}. {self.title}"

    @classmethod
    def send_email_as_a_task(cls,
                             email_type=None,
                             from_user=None,
                             context=None,
                             template_name="",
                             subject="",
                             body="",
                             from_email="postmaster@kintyazilim.com",
                             to=None,
                             bcc=None,
                             connection=None,
                             attachments=None,
                             headers=None,
                             alternatives=None,
                             cc=None,
                             reply_to=None):
        render_html = render_to_string(os.path.join(BASE_DIR, "templates", "email_templates", template_name), context)

        msg = EmailMultiAlternatives(subject,
                                     strip_tags(render_html),
                                     from_email=from_email,
                                     to=to,
                                     bcc=bcc,
                                     cc=cc,
                                     headers=headers,
                                     alternatives=alternatives,
                                     reply_to=reply_to,
                                     connection=connection
                                     )
        if attachments and isinstance(attachments, list):
            for attachment in attachments:
                try:
                    msg.attach(attachment[0], attachment[1], attachment[2])
                except Exception as e:
                    logging.exception(str(e))

        msg.attach_alternative(render_html, "text/html")
        msg.send()

        if bcc and len(bcc) > 9:
            for i in range(0, len(bcc), 9):
                Mail.objects.create(
                    type=email_type,
                    title=subject,
                    text=render_html,
                    to_email=to,
                    from_email=from_email,
                    from_user=from_user,
                    template=template_name,
                    bcc=bcc[i:i + 9],
                    cc=cc
                )
        else:
            Mail.objects.create(
                type=email_type,
                title=subject,
                text=render_html,
                to_email=to,
                from_email=from_email,
                from_user=from_user,
                template=template_name,
                bcc=bcc,
                cc=cc
            )
