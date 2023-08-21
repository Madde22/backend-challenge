import logging

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from mail.filters import MailFilter
from mail.models import Mail
from mail.serializers import MailSerializer
from utils.constants import CUSTOMER, VENDOR
from utils.permissions import IsSuperuser, IsOwner
from utils.util import MyModelViewSet

logger = logging.getLogger("default")


class MailViewSet(MyModelViewSet):
    queryset = Mail.objects.filter(is_deleted=False)

    serializer_class = MailSerializer
    filterset_class = MailFilter

    ordering_fields = ['id', 'type', 'title']
    search_fields = ['id', 'type', 'title']
    lookup_field = 'pk'

    permission_classes = []
    paginate_by_param = 'page_size'
    CACHE_KEY_PREFIX = "mail-view"

    permission_classes_per_method = {
        # except for list and retrieve where both users with "write" or "read-only"
        # permissions can access the endpoints.
        "list": [IsAuthenticated],
        "retrieve": [IsAuthenticated],
        "post": [IsAuthenticated],
        "create": [IsAuthenticated],
        "update": [IsSuperuser | IsOwner],
        "partial_update": [IsSuperuser | IsOwner],
        "destroy": [IsSuperuser],
    }

    def get_serializer_class(self):
        return MailSerializer

    def get_queryset(self):
        return self.queryset
