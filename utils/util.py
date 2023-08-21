import logging
import os
import random
from datetime import datetime
from random import randint

import requests
from PIL import Image
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from dotenv import load_dotenv
from drf_yasg import openapi
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import parsers
from rest_framework import status, filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from mysite.settings import MEDIA_ROOT
from utils.pagination import StandardResultsSetPagination
from utils.parsers import MultipartJsonParser
from utils.permissions import PermissionPolicyMixin, IsSuperuser
from utils.schemas import destroy_all_request_body, destroy_all_response_body

load_dotenv()

logger = logging.getLogger("default")

os.environ["TZ"] = "UTC"

naive_datetime = datetime.now()
aware_datetime = make_aware(naive_datetime)

CONTENT_TYPES = ['image', 'video']
MAX_UPLOAD_SIZE = "20971520"

extension_dict = {
    'pdf': "pdf.png",
    'doc': "word.png",
    'docx': "word.png",
    'xlsx': "excel.png",
    'mp3': "mp3.png",
    'wav': "wav.png",
    'mp4': "mp4.png",
    "video": "video.png",
    "audio": "audio.png"
}


class EnablePartialUpdateMixin:
    """
    Enable partial updates
    """

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class MyModelViewSet(PermissionPolicyMixin, EnablePartialUpdateMixin, viewsets.ModelViewSet):
    paginate_by_param = 'page_size'
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]
    parser_classes = (MultipartJsonParser, parsers.JSONParser)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    lookup_field = 'pk'
    ordering = ['-id']
    not_cached_models = ["Order", "User", "Address", "Basket", "Coupon", "Bank", "BankAddress", "Shipment", "Vendor",
                         "VendorFile", "VendorNote", "VendorComment", "ProductsSchema", "UploadedProductsSchema",
                         "UploadedProductsSchemaAttachment"]

    permission_classes_per_method = {
        # except for list and retrieve where both users with "write" or "read-only"
        # permissions can access the endpoints.
        "list": [],
        "retrieve": [],
        "create": [],
        "update": [],
        "partial_update": [],
        "destroy": [IsSuperuser],
    }

    def get_cached_data(self, request):
        model_name = self.get_serializer_class().Meta.model.__name__
        absolute_url = request.build_absolute_uri()
        hashed_absolute_url = hash(absolute_url)
        data = None
        self.queryset = self.get_queryset()
        if not request.user.is_authenticated:
            if model_name not in self.not_cached_models:
                data = cache.get(f"{model_name}_{hashed_absolute_url}")
                if data:
                    return data
        else:
            if model_name not in self.not_cached_models:
                data = cache.get(f"{model_name}_{hashed_absolute_url}_{request.user.id}")
                if data:
                    return data

        return None

    def list(self, request, *args, **kwargs):
        cached_data = self.get_cached_data(request)
        if cached_data:
            return Response(cached_data)

        model_name = self.get_serializer_class().Meta.model.__name__
        absolute_url = request.build_absolute_uri()
        hashed_absolute_url = hash(absolute_url)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            serialized_data = serializer.data
            response = self.get_paginated_response(serialized_data)

            if model_name not in self.not_cached_models:
                if request.user.is_authenticated:
                    data = cache.set(f"{model_name}_{hashed_absolute_url}_{request.user.id}", response.data)
                else:
                    data = cache.set(f"{model_name}_{hashed_absolute_url}", response.data)

            return response

        serializer = self.get_serializer(queryset, many=True)
        serialized_data = serializer.data

        if model_name not in self.not_cached_models:
            if request.user.is_authenticated:
                data = cache.set(f"{model_name}_{hashed_absolute_url}_{request.user.id}", serialized_data)
            else:
                data = cache.set(f"{model_name}_{hashed_absolute_url}", serialized_data)

        return Response(serialized_data)

    def retrieve(self, request, *args, **kwargs):
        model = self.serializer_class.Meta.model
        model_name = model.__name__

        cached_data = self.get_cached_data(request)
        if cached_data:
            return Response(cached_data)

        if isinstance(kwargs['pk'], int) or (isinstance(kwargs['pk'], str) and kwargs['pk'].isnumeric()):
            instance = self.queryset.filter(pk=kwargs['pk']).first()
        elif isinstance(kwargs['pk'], str) and hasattr(model, 'slug'):
            instance = self.queryset.filter(slug=kwargs['pk']).first()
        else:
            instance = None

        if instance:
            serializer = self.get_serializer(instance)

            absolute_url = request.build_absolute_uri()
            hashed_absolute_url = hash(absolute_url)

            if model_name not in self.not_cached_models:
                if request.user.is_authenticated:
                    data = cache.set(f"{model_name}_{hashed_absolute_url}_{request.user.id}", serializer.data)
                else:
                    data = cache.set(f"{model_name}_{hashed_absolute_url}", serializer.data)

            return Response(serializer.data)
        return Response({
            "detail": _("Not found.")
        }, status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @swagger_auto_schema(request_body=get_many_request_body)
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                description='Comma-separated list of IDs',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        ]
    )
    @action(
        detail=False,
        methods=['get'],
        url_path="get-many",
        url_name='get_many',
        permission_classes=[IsSuperuser]
    )
    def get_many_queryset(self, request, *args, **kwargs):
        model = self.serializer_class.Meta.model
        id_list = request.query_params.get('id')  # id parametresini alın
        ids = id_list.split(',') if id_list else []  # Virgülle ayrılmış stringi liste olarak ayırın

        if self.request.user.is_superuser:
            self.queryset = model.objects.filter(id__in=ids)
        else:
            self.queryset = None

        if self.queryset:
            serializer = self.get_serializer(self.queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({
                "detail": _("Not found.")
            }, status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    @action(detail=False, methods=['delete'], url_path="delete-many", url_name='delete_many',
            permission_classes=[IsSuperuser])
    @swagger_auto_schema(request_body=destroy_all_request_body, responses=destroy_all_response_body)
    def destroy_all(self, request, *args, **kwargs):
        deleted_items = []
        un_deleted_items = []
        self.queryset = self.queryset.filter(id__in=request.data["items"])
        if len(self.queryset) > 0:
            for pk in request.data["items"]:
                instance = self.queryset.filter(pk=pk).first()
                if instance and (request.user.is_superuser or
                                 (hasattr(instance, 'created_by') and instance.created_by == request.user) or
                                 (hasattr(instance, 'owner') and instance.owner == request.user)):
                    self.perform_destroy(instance)
                    deleted_items.append(instance)
                else:
                    un_deleted_items.append(pk)
            if len(un_deleted_items) == len(request.data["items"]):
                return Response({
                    "status": "error",
                    "message": _('Unauthorized attempts'),
                    "items": request.data["items"]
                },
                    status=status.HTTP_401_UNAUTHORIZED)
            else:

                return Response({
                    "status": "success",
                    "message": _('Destroying many items are successfull.'),
                    "delete_items": self.serializer_class(deleted_items, many=True).data,
                    "un_deleted_items": un_deleted_items
                },
                    status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                "status": "error",
                "message": _('entry not found'),
                "items": request.data["items"]
            },
                status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['role'] = user.role
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def clear_temp_files(files):
    """
    Delete temp file from media root
    """

    temp_files_set = set(files)

    for temp_file in temp_files_set:
        try:
            temp_path = os.path.join(MEDIA_ROOT, "temp", temp_file)
            os.remove(temp_path)
        except Exception as e:
            logging.exception(f"Error in deleting temp file = {e}")


def delete_cache(sender, instance):
    """
    Delete all cache keys with the given prefix.
    """
    try:
        cache.delete_pattern(f"{sender.__name__}*")
        if sender.__name__ == "Product":
            cache.delete('mainmenu')

        elif sender.__name__ == "Category":
            cache.delete('mainmenu')
            cache.delete('get_category')
            cache.delete(f'get_category_{instance.slug}')

        elif sender.__name__ == "Banner":
            cache.delete('get_banners' + str(instance.category))

        if sender.__name__ in ["Product", "Category", "Variant", "VariantValue",
                               "Spec", "SpecValue", "Brand", "Vendor"]:
            """
            Delete all main category es_ caches, and reset
            """
            cache.delete_pattern("es_*")
    except Exception as e:
        logging.exception(str(e))


def validate_recaptche(recaptcha_response):
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': os.getenv('GOOGLE_RECAPTCHA_SECRET_KEY'),
        'response': recaptcha_response
    }
    response = requests.post(url, data=values)
    result = response.json()
    return result['success']


def make_transparent(file):
    img = Image.open(file)
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(os.path.join(MEDIA_ROOT, "profiles", "avatar", "file2"), "PNG")


def get_client_ip(request):
    if request is None:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_device(request):
    return request.META['HTTP_USER_AGENT']


def get_next_id(model_class):
    items = model_class.objects.all().order_by('-id')
    if items.count() == 0:
        return 1
    return items[0].id + 1


default_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'


def get_random_string(length, allowed_chars=default_chars):
    random_string = ""
    for i in range(length):
        random_string += random.choice(allowed_chars)
    return random_string


def get_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return get_random_string(50, chars)


def two_weeks_hence():
    return timezone.now() + timezone.timedelta(days=14)


def one_month_hence():
    return timezone.now() + timezone.timedelta(days=30)


def one_year_hence():
    return timezone.now() + timezone.timedelta(days=365)


def ten_years_hence():
    return timezone.now() + timezone.timedelta(days=3650)


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]


def xml_escape(string):
    string = string.replace('&lt;![CDATA[', '')
    string = string.replace(']]&gt;', '')
    string = string.replace('&', '&amp;')
    return string


def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return None
    for x in a:
        if not x.isdigit():
            return None
        i = int(x)
        if i < 0 or i > 255:
            return None
    return s
