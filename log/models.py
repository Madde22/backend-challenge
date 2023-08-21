from django.db import models
from django.utils.translation import gettext_lazy as _


class AccessLog(models.Model):
    class Meta:
        verbose_name_plural = _('Access Log')
        verbose_name = _('Access Logs')
        db_table = "access_logs"
        ordering = ["pk"]

    sys_id = models.AutoField(primary_key=True, null=False, blank=True)
    session_key = models.CharField(max_length=1024, null=False, blank=True)
    path = models.CharField(max_length=1024, null=False, blank=True)
    method = models.CharField(max_length=8, null=False, blank=True)
    data = models.TextField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=False, blank=True)
    referrer = models.CharField(max_length=512, null=True, blank=True)
    timestamp = models.DateTimeField(null=False, blank=True)

    def __str__(self):
        return f"{self.sys_id}. {self.ip_address}"

