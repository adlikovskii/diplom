from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    ListAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .confirm import send_email
from .models import CustomUser, Contact, ConfirmToken
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CreateCustomUserSerializer,
    CreateContactSerializer,
    UpdateCustomUserSerializer,
    GetContactSerializer,
    UpdateContactSerializer,
)


class CreateCustomUserViewSet(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CreateCustomUserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["email", "first_name", "last_name"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.create_user(**serializer.validated_data)
        token = ConfirmToken.objects.create(user=user)
        send_email(user.email, token.token, [user.email])
        return JsonResponse(
            {
                "Success": "Account created successfully, please confirm your email"
            },
            status=status.HTTP_201_CREATED,
        )


class UpdateCustomUserViewSet(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = CustomUser.objects.all()
    serializer_class = UpdateCustomUserSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user  # проще так получить пользователя

        new_email = serializer.validated_data.get("email")
        if new_email and new_email != user.email:
            user.email = new_email
            user.is_active = False
            token = ConfirmToken.objects.create(user=user)
            send_email(new_email, token.token, [new_email])

        user.first_name = serializer.validated_data.get(
            "first_name", user.first_name
        )
        user.last_name = serializer.validated_data.get(
            "last_name", user.last_name
        )
        user.type = serializer.validated_data.get("type", user.type)

        new_password = serializer.validated_data.get("password")
        if new_password:
            user.set_password(new_password)

        user.save()
        return Response(
            {"Success": "Profile updated successfully"},
            status=status.HTTP_201_CREATED,
        )


class CreateContactView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = CreateContactSerializer


class GetContactView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetContactSerializer

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class UpdateContactView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Contact.objects.all()
    serializer_class = UpdateContactSerializer


class DeleteContactView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Contact.objects.all()


class ConfirmEmailView(ListAPIView):
    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        email = kwargs.get("email")

        if not token or not email:
            return Response(
                {"Error": "Token and email are required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            confirm_token = ConfirmToken.objects.get(
                token=token, user__email=email
            )
        except ConfirmToken.DoesNotExist:
            return Response(
                {"Error": "Invalid token or email"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = confirm_token.user
        user.is_active = True
        user.save()
        confirm_token.delete()

        return Response(
            {"Success": "Email confirmed successfully"},
            status=status.HTTP_201_CREATED,
        )
