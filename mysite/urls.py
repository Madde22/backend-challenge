from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenBlacklistView, TokenVerifyView,
)

from brewery.views import BreweriesViewSet
from mysite.schema import schema
from user.views import *
from utils.rest_router import OptionalSlashRouter
from utils.schemas import token_response_schema_dict, register_response_schema_dict
from graphene_django.views import GraphQLView
load_dotenv()

schema_view = get_schema_view(
    openapi.Info(
        title="madde22 API",
        default_version='v1',
        description="Test description",
        terms_of_service=os.getenv("SCHEMA_POLICIES"),
        contact=openapi.Contact(email="tekin@madde22.com"),
        license=openapi.License(name="BSD License"),
        base_url=os.getenv("SCHEMA_BASE_URL")
    ),
    url=os.getenv("SCHEMA_BASE_URL"),
    permission_classes=[permissions.AllowAny],
    public=True,
)

decorated_token_view = \
    swagger_auto_schema(
        method='post',
        responses=token_response_schema_dict
    )(CustomTokenObtainPairView.as_view())

decorated_customer_register_view = \
    swagger_auto_schema(
        method='post',
        request_body=RegisterSerializer(),
        responses=register_response_schema_dict
    )(RegisterApiView.as_view())

router = OptionalSlashRouter()

router.register(r'api/users', UserViewSet, basename='user')
router.register(r'api/breweries', BreweriesViewSet, basename='breweries')

handler404 = handler404
handler500 = handler500
handler501 = handler501

urlpatterns = [
    re_path(r"graphql", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),

    path('api/logout/', LogoutApiView.as_view(), name='logout_api_view'),
    path('api/register', decorated_customer_register_view, name='customer_register_api'),
    path('api/login/', decorated_token_view, name='api_login'),
    path('api/token/', decorated_token_view, name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/verify/email', VerifyApiView.as_view(), name='verify'),

    re_path(r'^sifremi-sifirla/$', reset_password, name="oscar_reset_password"),
    re_path(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$',
            my_password_reset_confirm, kwargs={'template_name': 'myregistration/password_reset_confirm.html'},
            name='password_reset_confirm'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(),
            {'template_name': 'myregistration/password_reset_done.html'}, name='password_reset_done'),
    re_path(r'^password_reset/complete/$',
            auth_views.PasswordResetCompleteView.as_view(template_name='myregistration/password_reset_complete.html'),
            name='password_reset_complete'),

    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$', ActivateView.as_view(),
            name='activate'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view().without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view().with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view().with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r"^favicon", RedirectView.as_view(url='/media/images/logo.png', permanent=True), name="favicon_view"),
    re_path(r'^django/static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT,
                                                     'show_indexes': settings.DEBUG}),
    re_path(r'^django/media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,
                                                    'show_indexes': settings.DEBUG}),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', schema_view().with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += i18n_patterns(path('admin/', admin.site.urls))
urlpatterns += router.urls
