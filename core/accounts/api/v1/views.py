import sys
from accounts.models import User
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from .serializers import RegisterSerializer ,LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate , login ,logout
class AuthUserViewSet(GenericViewSet):
    """
    a class for user authentication action (register , login , logout)
    """
    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterSerializer
        elif self.action == 'login':
            return LoginSerializer
    @action(methods=['POST'] ,detail=False)
    def register(self ,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = User.objects.create_user(
                email=email,
                password=password
            )
            authenticate(request ,email=email , password=password)
            login(request , user)
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'] ,detail=False)
    def login(self ,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = User.objects.get(email=email)
            authenticate(request ,email=email , password=password)
            login(request ,user)
            return Response(serializer.data , status=status.HTTP_200_OK)
        return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET",],detail=False)
    def logout(self, request):
        logout(request)
        return Response(data='User logged out', status=status.HTTP_200_OK)