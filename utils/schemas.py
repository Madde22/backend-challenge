from django.utils.translation import gettext as _
from drf_yasg import openapi

forget_password_response_schema_dict = {
    400: _("Bad Request"),
    500: _("Internal Server Error"),
    200: openapi.Response(
        description="A link to reset user password is sent into user's email address",
        examples={
            "application/json": {
                "success": True,
                "message": _("User can reset his/her password via reset link sent into his/her email address.")
            }
        }
    ),
}

forget_password_done_response_schema_dict = {
    400: _("Bad Request"),
    500: _("Internal Server Error"),
    200: openapi.Response(
        description="User's email reset done",
        examples={
            "application/json": {
                "success": True,
                "message": _("User's password has changed.")
            }
        }
    ),
}

forget_password_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    content="application/json",
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description="string: user's registered email."),

    })

forget_password_done_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    content="application/json",
    properties={
        'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="string: user's new_password."),
        'uid': openapi.Schema(type=openapi.TYPE_STRING, description="string: user's encrypted user id."),
        'token': openapi.Schema(type=openapi.TYPE_STRING,
                                description="string: user's one time consumed link for one day"),
    })

password_change_response_schema_dict = {
    400: _("Bad Request"),
    201: openapi.Response(
        description="User password is changed successfully",
        examples={
            "application/json": {
                "refresh": "eyJhbG.eyJ0b2tlblY2QwZjVmYyIsInVzZXJfaWQiOjE4fQ.LPt_XnLC6KWtNE",
                "access": "eyJhbVCJ9.eyJ0b2tlbl9Dc2LCJpYXQiOjE2NjXNlcl9pZCI6MTh9.K6UPz8V0LTxm3qnI",
            }
        }
    )
}

token_response_schema_dict = {
    400: _("Bad Request"),
    201: openapi.Response(
        description="New JWT (JSON Web Token) is created successfully",
        examples={
            "application/json": {
                "refresh": "eyJhbG.eyJ0b2tlblY2QwZjVmYyIsInVzZXJfaWQiOjE4fQ.LPt_XnLC6KWtNE",
                "access": "eyJhbVCJ9.eyJ0b2tlbl9Dc2LCJpYXQiOjE2NjXNlcl9pZCI6MTh9.K6UPz8V0LTxm3qnI",
            }
        }
    )
}

register_response_schema_dict = {
    400: _("Bad Request"),
    201: openapi.Response(
        description="New User is created "
                    "successfully",
        examples={
            "application/json": {
                "access": "JWT TOKEN",
                "refresh": "Refresh TOKEN",
            }
        }
    ),
}

verification_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'uid': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    })

get_many_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'ids': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    })

verification_response_schema_dict = {
    400: _("Bad Request"),
    200: openapi.Response(
        description="Email address is verified successfully",
        examples={
            "application/json": {
                "success": True,
                "message": _("User's email was verified successfully.")
            }
        }
    ),
}


change_password_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    content="application/json",
    properties={
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='string: new password'),
        're_password': openapi.Schema(type=openapi.TYPE_STRING, description='string: new password again'),
        'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='string: user old password'),
    })
order_create_response_schema_dict = {
    400: _("Bad Request"),
    500: _("Internal Server Error"),
    201: openapi.Response(
        description="New order is created",
        examples={
            "application/json": {
                "success": True,
                "message": _("User has bought everthing in his/her basket successfully.")
            }
        }
    ),
}

destroy_all_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    content="application/json",
    properties={
        "items": openapi.Schema(type=openapi.TYPE_ARRAY, items={"type": "int", })}
)

destroy_all_response_body = {
    400: _('Destroying many items are un-successfull.'),
    500: _(_("Internal Server Error")),
    204: _('Destroying many items are successfull.')
}

upload_response_schema_dict = {
    400: _("Bad Request"),
    500: _("Internal Server Error"),
    201: openapi.Response(
        description="File upload is successfull",
        examples={
            "application/json": [
                {
                    "id": 262,
                    "thumbnail": None,
                    "original": "https://cdn.madde22.com/images/20221118/2022_11_18_09_16_45_xxxx.png"
                }
            ]
        }
    ),
}

user_me_response_schema_dict = {
    400: _("Bad Request"),
    200: openapi.Response(
        description="Vendor Profile",
        examples={
            "application/json": {
                "id": 7,
                "username": "c.topuz@yahoo.com",
                "email": "c.topuz@yahoo.com",
                "tckn": "00000000000",
                "full_name": "Cuma TOPUZ",
                "first_name": "Cuma",
                "last_name": "TOPUZ",
                "phone": None,
                "role": "customer",
                "is_email_verified": False,
                "email_verified_at": "2022-11-28T12:54:12+03:00",
                "is_mobile_verified": False,
                "mobile_verified_at": None,
                "date_joined": "2022-11-28T12:48:40+03:00",
                "madde22_sms_allowed": True,
                "madde22_email_allowed": True,
                "madde22_phone_allowed": True,
                "addresses": [
                    {
                        "id": 5,
                        "owner": 7,
                        "title": "Ev Adresim",
                        "country": {
                            "id": 225,
                            "name": "Turkey",
                            "iso2": "TR",
                            "iso3": "TUR",
                            "flag": {
                                "id": 228,
                                "slug": None,
                                "thumbnail": "https://cdn.madde22.com/flags/thumbnails/tr.svg",
                                "original": "https://cdn.madde22.com/flags/originals/tr.svg"
                            }
                        },
                        "state": None,
                        "city": None,
                        "il": {
                            "id": 6,
                            "name": "Ankara"
                        },
                        "ilce": {
                            "id": 58,
                            "il": 68,
                            "name": "Sultanhanı"
                        },
                        "mahalle_koy": {
                            "id": 3316,
                            "name": "Uğrak Mah. (Mescitköy Köyü)",
                            "ilce": 44,
                            "ilce_name": "Doğubayazıt",
                            "il_name": "Ağrı",
                            "posta_kodu": "04402"
                        },
                        "street_address": "Macun Mah. Bağdat Cad Ece İş Merkezi, D:95A/7, 06374 Yenimahalle/Ankara",
                        "first_name": "Tekin",
                        "last_name": "TOPUZ",
                        "mobile_phone": "5536858122",
                        "tckn": "17501613***",
                        "vkn": None,
                        "company_name": None,
                        "vergi_dairesi": None,
                        "e_fatura_mukellefiyim": False,
                        "pasaport_no": "175016****",
                        "is_active": True,
                        "is_current": True,
                        "posta_kodu": "04402",
                        "fatura_type": "Bireysel"
                    }
                ],
                "is_active": True,
                "is_deleted": False,
                "deleted_at": "2022-11-28T12:48:40+03:00",
                "last_login": "2023-02-07T09:24:22.521055+03:00"
            }
        })
}

my_products_response_schema_dict = {
    400: _("Bad Request"),
    200: openapi.Response(
        description="Vendor All Products",
        examples={
            "application/json": {
                "success": True,
                "message": _("Vendor's all product will be put in an excel file for her/him to download.")
            }
        }
    ),
}