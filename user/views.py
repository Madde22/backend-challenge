import logging
import os
import sys
from collections import OrderedDict

from django.contrib.auth import login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, resolve_url
from django.template import loader
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from dotenv import load_dotenv
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import parsers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from mail.tasks import send_email_as_a_task
from mysite.settings import EMAIL_ACTIVATION_URL, FRONTEND_FORGET_PASSWORD_URL
from user.filters import UserFilter
from user.models import User
from user.serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer, \
    UserChangePasswordSerializer, \
    UserMeSerializer, PasswordDoneSerializer
from user.token import account_activation_token
from utils.constants import REGISTRATION_EMAIL, PASSWORD_RESET_EMAIL
from utils.parsers import MultipartJsonParser
from utils.permissions import IsSuperuser
from utils.schemas import verification_request_body, verification_response_schema_dict, \
    password_change_response_schema_dict, change_password_body, forget_password_body, \
    forget_password_response_schema_dict, forget_password_done_body, forget_password_done_response_schema_dict, \
    user_me_response_schema_dict
from utils.util import MyModelViewSet, validate_recaptche
import requests

load_dotenv()


def handler404(request, exception="", template_name='errors/errorPage404.html'):
    type_, value, traceback = sys.exc_info()
    context = {
        "name": "404",
        "message": f"PAGE NOT FOUND! {value}"
    }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request), status=404)


def handler500(request, exception="", template_name='errors/errorPage500.html'):
    type_, value, traceback = sys.exc_info()
    context = {
        "name": "500",
        "message": f"500 Internal Server Error !=== > {value}"
    }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request), status=500)


def handler501(request, exception="", template_name='errors/errorPage501.html'):
    type_, value, traceback = sys.exc_info()
    context = {
        "name": "501",
        "message": f"501 Not Implemented !=== > {value}"
    }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


"""
Ayrıca users'ta da fullname email ve id ile yapmak istiyorum şuan yapabilir durumda mıyım ?
"""


class UserViewSet(MyModelViewSet):
    queryset = User.objects.filter(is_active=True, is_deleted=False)
    serializer_class = UserSerializer

    filterset_class = UserFilter
    CACHE_KEY_PREFIX = "user-view"
    ordering_fields = ['id', 'email', 'is_active', 'is_staff',
                       'first_name', 'last_name', 'full_name']
    search_fields = ['id', 'email', 'is_active', 'is_staff', 'first_name', 'last_name', 'full_name']
    lookup_field = 'pk'

    permission_classes_per_method = {
        # except for list and retrieve where both users with "write" or "read-only"
        # permissions can access the endpoints.
        "list": [IsSuperuser],
        "retrieve": [IsSuperuser],
        "create": [IsSuperuser],
        "update": [IsSuperuser],
        "partial_update": [IsSuperuser],
        "destroy": [IsSuperuser],
    }

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        If a user doesn't send required areas, it means that partial update
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    """
    Admin istatistik apisi için :  Toplam tedarikçi, Toplam ürün, Toplam sipariş, Toplam kullanıcı, onay bekleyen vendor 
     ve onay bekleyen ürün sayılarına ihtiyacım var. 
     Birde grafik için son bir haftalık siparişler içerisinden toplam sipariş, 
     iptal edilen sipariş ve iade edilen sipariş sayılarına ihtiyacım var. 
     Müsait olduğunuzda bakabilir misiniz acaba ?
    """

    @action(detail=False, methods=['get'], url_path="me", permission_classes=[IsSuperuser])
    @swagger_auto_schema(responses=user_me_response_schema_dict)
    def me(self, request, pk=None, *args, **kwargs):
        serializer_context = {'request': request}
        me_json = UserSerializer(instance=request.user, context=serializer_context).data
        return Response(me_json)

    @action(detail=False, methods=['put'], url_path="me/update", permission_classes=[IsSuperuser])
    @swagger_auto_schema(request_body=UserMeSerializer,
                         responses=user_me_response_schema_dict)
    def me_update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = request.user
        serializer = UserMeSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(UserMeSerializer(instance).data)

    @transaction.atomic
    @action(detail=False, methods=['put'], url_path="change-password", permission_classes=[IsAuthenticated])
    @swagger_auto_schema(request_body=change_password_body,
                         responses=password_change_response_schema_dict)
    def change_password(self, request, pk=None, *args, **kwargs):

        if request.user.is_superuser and "user" in request.data:
            member = User.objects.get(pk=request.data["user"])
            member.set_password(request.data.get("password"))
            member.save()
            od = OrderedDict()
            od["email"] = member.email
            od["password"] = request.data['password']

            return Response(CustomTokenObtainPairSerializer().validate(od))
        else:
            member = request.user

            serializer = UserChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                # Check old password
                if not member.check_password(serializer.data.get("old_password")):
                    return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
                # set_password also hashes the password that the user will get
                member.set_password(serializer.data.get("password"))
                member.save()

                od = OrderedDict()
                od["email"] = member.email
                od["password"] = serializer.validated_data['password']

                return Response(CustomTokenObtainPairSerializer().validate(od))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path="forget-password", permission_classes=[])
    @swagger_auto_schema(request_body=forget_password_body,
                         responses=forget_password_response_schema_dict)
    def forget_password(self, request, pk=None, *args, **kwargs):
        if "email" not in request.data:
            return Response({
                "status": "error",
                "message": _(f"User email must be sent.")
            }, status=status.HTTP_400_BAD_REQUEST)

        email = request.data["email"]
        member = User.objects.filter(email=email).first()

        if member:
            """
            Be sure about if role is vendor and there must be a vendor instance for that user
            """

            self.send_password_reset_email(member)
            return Response({
                "status": "success",
                "message": _("A password reset link is sent into your email address.")})

        return Response({
            "status": "error",
            "message": _(f"There is no user with this email.")
        }, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path="forget-password-done", permission_classes=[])
    @swagger_auto_schema(request_body=forget_password_done_body,
                         responses=forget_password_done_response_schema_dict)
    def forget_password_done(self, request, pk=None, *args, **kwargs):
        serializer = PasswordDoneSerializer(data=request.data)
        if serializer.is_valid():
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.filter(pk=uid).first()
            if user is not None and default_token_generator.check_token(user, serializer.validated_data["token"]):
                user.set_password(serializer.validated_data["new_password"])
                user.is_active = True
                user.save()
                login(request, user)
                return Response({
                    "status": "success",
                    "message": _(f"User has reset his password.")
                })

            return Response({
                "status": "error",
                "message": _(f"There is no user with this email or link is expired")
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_password_reset_email(self, user):

        frontend_url = FRONTEND_FORGET_PASSWORD_URL

        context = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            "FRONTEND_URL": frontend_url
        }
        send_email_as_a_task(email_type=PASSWORD_RESET_EMAIL,
                             context=context,
                             subject=os.getenv("PASSWORD_RESET_SUBJECT"),
                             template_name=os.getenv("PASSWORD_RESET_TEMPLATE"),
                             to=[user.email]
                             )


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]
    serializer_class = CustomTokenObtainPairSerializer


class ActivateView(View):
    def get(self, request, uidb64=None, token=None):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.filter(pk=uid).first()
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_activated = True
            user.email_verified_at = timezone.now()
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            template = loader.get_template('myregistration/activation_email_complete.html')
            return HttpResponse(template.render({}, request))
        else:
            template = loader.get_template('myregistration/activation_email_error.html')
            return HttpResponse(template.render({}, request))


class VerifyApiView(APIView):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]

    @swagger_auto_schema(request_body=verification_request_body, responses=verification_response_schema_dict)
    def put(self, request):
        uid = force_str(urlsafe_base64_decode(request.data["uid"]))
        token = request.data["token"]

        user = User.objects.filter(pk=uid).first()
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.is_email_activated = True
            user.email_activated_at = timezone.now()
            user.save()

            return Response({
                "success": True,
                "message": _("User's email was verified successfully.")
            })
        return Response({
            "success": False,
            "message": _("The link expired or there is no such a user.")
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if "refresh" not in request.data:
            return Response(data="Refresh token must be sent for logging out ", status=status.HTTP_400_BAD_REQUEST)
        try:
            # token = AccessToken(request.auth.token)
            refresh_token = RefreshToken(request.data["refresh"])
            refresh_token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR, )


class RegisterApiView(APIView):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()

            self.send_activation_email(new_user)

            customer_group, created = Group.objects.get_or_create(name="Customer")
            customer_group.user_set.add(new_user)

            od = OrderedDict()
            od["email"] = serializer.validated_data['email']
            od["password"] = serializer.validated_data['password']

            data = CustomTokenObtainPairSerializer().validate(od)
            data["message"] = _(
                "User was created successfully and an email verification was sent registered email address.")

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_activation_email(self, user):
        context = {
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            "FRONTEND_URL": EMAIL_ACTIVATION_URL
        }

        send_email_as_a_task(email_type=REGISTRATION_EMAIL,
                             context=context,
                             subject=os.getenv("EMAIL_ACTIVATION_SUBJECT"),
                             template_name=os.getenv("EMAIL_ACTIVATION_TEMPLATE"),
                             to=[user.email]
                             )


def reset_password(request):
    if request.method == "POST":
        if True or validate_recaptche(request.POST.get('g-recaptcha-response')):
            email = request.POST.get('email', '')
            try:
                user = User.objects.filter(Q(username=email) | Q(email=email)).first()
                if not user:
                    context = {"status": "error", "message": "Böyle Bir Kullanıcı yok!"}
                    template = loader.get_template('madde22/login.html')
                    return HttpResponse(template.render(context, request))

                c = {
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email_subject_name = 'myregistration/password_reset_subject.txt'
                email_template_name = 'myregistration/password_reset_email.html'
                render_html = render_to_string(email_template_name, c)
                render_subject = render_to_string(email_subject_name, c)

                msg = EmailMultiAlternatives(render_subject, strip_tags(render_html), "info@oscararastirma.com",
                                             [user.email])
                msg.attach_alternative(render_html, "text/html")
                msg.send()
                context = {"status": "success", "message": "Şifre Sıfırlama link şu anda eposta adresinize gönderildi."}
                template = loader.get_template('madde22/login.html')
                return HttpResponse(template.render(context, request))
            except Exception as e:
                context = {"status": "error", "message": "Böyle Bir Kullanıcı yok!==> " + str(e)}
                template = loader.get_template('madde22/login.html')
                return HttpResponse(template.render(context, request))
        else:
            context = {"status": "error", "message": "Lütfen recaptche yi doğrulayınız.."}
            template = loader.get_template('madde22/login.html')
            return HttpResponse(template.render(context, request))
    else:
        return redirect("login")


@sensitive_post_parameters()
@never_cache
def my_password_reset_confirm(request, uidb64=None, token=None,
                              template_name='registration/password_reset_confirm.html',
                              token_generator=default_token_generator,
                              set_password_form=SetPasswordForm,
                              post_reset_redirect=None,
                              extra_context=None):
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    uid = urlsafe_base64_decode(uidb64)
    user = User.objects.filter(pk=uid).first()
    context = {}
    if user and token_generator.check_token(user, token):
        validlink = True
        title = 'Enter new password'
        if request.method == 'POST':
            form = set_password_form(user, request.POST)

            if form.is_valid():
                try:
                    user.profile.raw_pwd = request.POST.get("new_password1")
                    user.profile.save()
                except Exception as e:
                    logging.exception(f"User = {uid} has not profile . [{e}]")
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
            else:
                error = ""
                for k, v in form.errors.items():
                    if len(v) > 0:
                        error = v[0]
                        break
                    else:
                        error = "Bir Hata Oluştu bilgilerinizi kontrol ediniz."
                        break
                context['title'] = title
                context['validlink'] = validlink
                context['status'] = "error"
                context['message'] = error
        else:
            form = set_password_form(user)
        context['title'] = title
        context['validlink'] = validlink
    else:
        validlink = False
        form = None
        title = 'Password reset unsuccessful'
        context['form'] = form
        context['title'] = title
        context['validlink'] = validlink
        context['status'] = "error"
        context['message'] = "Bu link çalışmıyor-zamanı geçmiş olabilir."

    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)



