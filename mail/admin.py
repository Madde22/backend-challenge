from django.contrib import admin

from mail.models import Mail


class MailAdmin(admin.ModelAdmin):
    search_fields = ('id', 'title', 'text', 'to_email')


admin.site.register(Mail, MailAdmin)
