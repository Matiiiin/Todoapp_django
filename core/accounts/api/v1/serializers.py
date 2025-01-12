import jwt
from rest_framework import serializers
from accounts.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

auth_model = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        if data.get("password1") != data.get("password2"):
            raise serializers.ValidationError(
                "password and its confirmation should be the same"
            )
        if User.objects.filter(email=data.get("email")).exists():
            raise serializers.ValidationError(
                "a user with the same email already exists"
            )
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        email = data.get("email")
        password = data.get("password")
        authenticated_user = authenticate(username=email, password=password)
        if not authenticated_user:
            raise serializers.ValidationError(
                {
                    "detail": "Invalid credentials , maybe password or email is incorrect"
                }
            )
        if not authenticated_user.is_verified:
            raise serializers.ValidationError(
                {"detail": "Provided user is not verified"}
            )
        data["authenticated_user"] = authenticated_user
        return data


class JWTCreateSerializer(serializers.Serializer):
    username_field = get_user_model().USERNAME_FIELD

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(
            write_only=True
        )
        self.fields["password"] = serializers.CharField(
            write_only=True, max_length=255
        )

    def validate(self, attrs):
        data = super().validate(attrs)
        username_field = data.get(self.username_field)
        password = data.get("password")
        authenticate_user = authenticate(
            username=username_field, password=password
        )
        if not authenticate_user:
            raise serializers.ValidationError(
                {"detail": "Invalid credentials"}
            )
        if not authenticate_user.is_verified:
            raise serializers.ValidationError(
                {"detail": "Provided user is not verified"}
            )
        data["authenticated_user"] = authenticate_user
        return data


class JWTRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=500)

    def validate(self, attrs):
        data = super().validate(attrs)
        try:
            payload = jwt.decode(
                jwt=attrs.get("refresh"),
                key=settings.SECRET_KEY,
                algorithms=["HS256"],
            )
            if not get_object_or_404(
                User, pk=payload.get("user_id")
            ).is_verified:
                raise serializers.ValidationError(
                    {"detail": "The user for provided token is not verified"}
                )
            refresh = RefreshToken(attrs.get("refresh"))
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            data["access"] = str(refresh.access_token)
            return data
        except TokenError as e:
            raise serializers.ValidationError({"detail": e})
        except jwt.exceptions.InvalidSignatureError as e:
            raise serializers.ValidationError({"detail": e})
        except jwt.exceptions.DecodeError as e:
            raise serializers.ValidationError({"detail": e})
        except jwt.exceptions.ExpiredSignatureError as e:
            raise serializers.ValidationError({"detail": e})


class VerifyAccountResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ForgetPasswordConfirmSerializer(serializers.Serializer):
    temporary_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        url_token = self.context.get("request").resolver_match.kwargs.get(
            "token"
        )
        token = jwt.decode(
            url_token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user = get_object_or_404(User, pk=token.get("user_id"))
        if not user.is_verified:
            raise serializers.ValidationError(
                {"detail": "You are not verified"}
            )
        if not user.check_password(attrs.get("temporary_password")):
            raise serializers.ValidationError(
                {"detail": "Temporary password is incorrect"}
            )
        data["user"] = user
        return data


class CustomTokenLoginSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                username=email,
                password=password,
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError({'detail':msg}, code="authorization")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError({'detail':msg}, code="authorization")

        attrs["user"] = user
        return attrs
