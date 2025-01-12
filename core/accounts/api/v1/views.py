import json
import os
from accounts.models import User
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import (
    RegisterSerializer,
    CustomTokenLoginSerializer,
    ForgetPasswordConfirmSerializer,
    ForgetPasswordSerializer,
    VerifyAccountResendSerializer,
    LoginSerializer,
    JWTCreateSerializer,
    JWTRefreshSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from jwt.exceptions import (
    InvalidSignatureError,
    ExpiredSignatureError,
    DecodeError,
)
from django.conf import settings
from accounts.utils import RabbitMQConnection
import uuid
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class AuthUserViewSet(GenericViewSet):
    """
    a class for user authentication action (register , login , logout)
    """

    def get_serializer_class(self):
        if self.action == "register":
            return RegisterSerializer
        elif self.action == "login":
            return LoginSerializer

    def get_permissions(self):
        if self.action == "logout":
            return [IsAuthenticated()]
        return []

    @swagger_auto_schema(
        method="post",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                "User registered successfully", RegisterSerializer
            ),
            400: "Validation errors",
        },
    )
    @action(methods=["POST"], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password1")
            user = User.objects.create_user(email=email, password=password)
            login(request, user)
            token = RefreshToken.for_user(user)
            verification_email_body = render_to_string(
                "email/user_verification.html", context={"token": token}
            )

            # using django built in email
            # email = EmailMessage(
            #     "User verification email",
            #     verification_email_body,
            #     "admin@todoapp.com",
            #     [user.email],
            # )
            # email.send(fail_silently=True)

            # using a sender service
            broker_message_body = {
                "email_body": verification_email_body,
                "sender": "admin@todoapp.com",
                "recipients": [user.email],
                "subject": "User verification email",
            }
            rabbitmq = RabbitMQConnection(
                host=os.getenv("RABBITMQ_HOST"),
                username=os.getenv("RABBITMQ_USER"),
                password=os.getenv("RABBITMQ_PASS"),
            )
            rabbitmq.channel.exchange_declare(
                exchange="email", exchange_type="direct", durable=True
            )
            rabbitmq.channel.queue_declare("send_email", durable=True)
            rabbitmq.channel.basic_publish(
                exchange="email",
                routing_key="send_email",
                body=json.dumps(broker_message_body),
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method="post",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                "User logged in successfully", LoginSerializer
            ),
            400: "Validation errors or authentication failed",
        },
    )
    @action(methods=["POST"], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            login(request, serializer.validated_data.get("authenticated_user"))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method="post",
        responses={
            200: "User logged out successfully",
        },
    )
    @action(
        methods=[
            "POST",
        ],
        detail=False,
    )
    def logout(self, request):
        logout(request)
        return Response(
            data={"detail": "User logged out successfully"},
            status=status.HTTP_200_OK,
        )


class JWTCreateView(GenericAPIView):
    """
    Create a JWT token for user
    """

    serializer_class = JWTCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            refresh_token = RefreshToken.for_user(
                serializer.validated_data.get("authenticated_user")
            )
            data = {
                "access_token": str(refresh_token.access_token),
                "refresh_token": str(refresh_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTRefreshView(GenericAPIView):
    """
    Refresh the access token for provided refresh token
    """

    serializer_class = JWTRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = {"access": serializer.validated_data.get("access")}
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenLoginView(ObtainAuthToken):
    """
    login with a generated token for user in database
    """

    serializer_class = CustomTokenLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "email": user.email},
            status=status.HTTP_200_OK,
        )


class CustomTokenLogoutView(APIView):
    """
    delete the token and log out from application
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response(
                {"detail": "User logged out successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"detail": e}, status=status.HTTP_400_BAD_REQUEST)


class VerifyAccountView(GenericAPIView):
    """
    Verify User with incoming generated JWT
    """

    def get(self, request, token):
        try:
            token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = get_object_or_404(User, pk=token.get("user_id"))
            if user.is_verified:
                return Response({"detail": "Your account is verified before"})
            user.is_verified = True
            user.save()
            return Response(
                {"detail": "User activated successfully"},
                status=status.HTTP_200_OK,
            )
        except ExpiredSignatureError:
            return Response(
                {"detail": "Your token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"detail": "Your token is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DecodeError:
            return Response(
                {"detail": "Your JWT token doesnt have enough segments"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyAccountResendView(GenericAPIView):
    """
    Send a new verification email to user
    """

    serializer_class = VerifyAccountResendSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User, email=serializer.validated_data.get("email")
            )
            if user.is_verified:
                return Response({"detail": "You are verified before"})
            token = RefreshToken.for_user(user)
            verification_resend_email_body = render_to_string(
                "email/user_verification_resend.html",
                context={"token": token},
            )
            broker_message_body = {
                "email_body": verification_resend_email_body,
                "sender": "admin@todoapp.com",
                "recipients": [user.email],
                "subject": "User verification resend email",
            }
            rabbitmq = RabbitMQConnection(
                host=os.getenv("RABBITMQ_HOST"),
                username=os.getenv("RABBITMQ_USER"),
                password=os.getenv("RABBITMQ_PASS"),
            )
            rabbitmq.channel.exchange_declare(
                exchange="email", exchange_type="direct", durable=True
            )
            rabbitmq.channel.queue_declare("send_email", durable=True)
            rabbitmq.channel.basic_publish(
                exchange="email",
                routing_key="send_email",
                body=json.dumps(broker_message_body),
            )
            return Response(
                {"detail": "Verification email has been sent"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(GenericAPIView):
    """
    class for getting user email and send temporary pass for resetting the password
    """

    serializer_class = ForgetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User, email=serializer.validated_data.get("email")
            )
            temp_password = uuid.uuid4().hex[:10].upper()
            user.set_password(temp_password)
            user.save()
            token = RefreshToken.for_user(user)
            reset_password_email_body = render_to_string(
                "email/forgot_password.html",
                context={"password": temp_password, "token": token},
            )
            broker_message_body = {
                "email_body": reset_password_email_body,
                "sender": "admin@todoapp.com",
                "recipients": [user.email],
                "subject": "User forget password email",
            }
            rabbitmq = RabbitMQConnection(
                host=os.getenv("RABBITMQ_HOST"),
                username=os.getenv("RABBITMQ_USER"),
                password=os.getenv("RABBITMQ_PASS"),
            )
            rabbitmq.channel.exchange_declare(
                exchange="email", exchange_type="direct", durable=True
            )
            rabbitmq.channel.queue_declare("send_email", durable=True)
            rabbitmq.channel.basic_publish(
                exchange="email",
                routing_key="send_email",
                body=json.dumps(broker_message_body),
            )
            return Response(
                {"detail": "Reset password email has been sent"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordConfirmView(GenericAPIView):
    """
    submitting the new pass provided by user in database
    """

    serializer_class = ForgetPasswordConfirmSerializer

    def post(self, request, token):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            new_password = serializer.validated_data.get("new_password")
            user.set_password(new_password)
            user.save()
            return Response(
                {"detail": "User password was reset successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
