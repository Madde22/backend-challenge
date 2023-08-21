import logging
import os

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from dotenv import load_dotenv

from mysite.celery import app
from mysite.settings import BASE_DIR
from mail.models import Mail

load_dotenv()


# @app.task
def send_email_as_a_task(email_type=None,
                         from_user=None,
                         context=None,
                         template_name="",
                         subject="",
                         body="",
                         from_email=os.getenv("DEFAULT_FROM_EMAIL"),
                         to=None,
                         bcc=None,
                         connection=None,
                         attachments=None,
                         headers=None,
                         alternatives=None,
                         cc=None,
                         reply_to=None,
                         order_num=None,
                         my_attachments=None,
                         vendor=None,
                         customer=None,
                         created_by=None
                         ):
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
    # if attachments and isinstance(attachments, list):
    #     for attachment in attachments:
    #         try:
    #             msg.attach(attachment[0], attachment[1], attachment[2])
    #         except Exception as e:
    #             logging.exception(str(e))
    # msg.attach_alternative(render_html, "text/html")
    # msg.send()
    if bcc:
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
            cc=cc
        )

    # if my_attachments and isinstance(my_attachments, list):
    #     for my_attachment in my_attachments:
    #         mail.attachments.add(my_attachment)
