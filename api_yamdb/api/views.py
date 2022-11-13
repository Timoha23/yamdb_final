
from random import randint

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND)
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from title.models import Category, Genre, Title
from users.models import User

from api.paginator import CommentPagination
from api.permissions import (IsAdminOrAuthorOrReadOnly,
                             IsAdminOrReadOnly, AdminOnly)
from api.serializers import CommentsSerializer, ReviewsSerializer

from .serializers import (CategorySerializer, GenreSerializer,
                          TitleCreateSerializer, TitleSerializer,
                          UserGetTokenSerializer, UserSerializer,
                          UserSignUpSerializer)
from .filter import TitleFilter


class UserSignUp(APIView):
    """Регистрация юзера"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)

        # Если юзера нет в базе
        if serializer.is_valid():
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            confirmation_code = randint(1000, 999999)
            User.objects.create(
                username=username,
                email=email,
                confirmation_code=confirmation_code
            )
            send_mail(
                'Письмо с кодом верификации',
                f'Код: {confirmation_code}',
                'from@example.com',
                [serializer.data.get('email')]
            )
            return Response(serializer.data, status=HTTP_200_OK)

        # Если юзер есть в базе, но конфирм кода нет (зареган админом)
        elif User.objects.filter(username=serializer.data.get('username'),
                                 email=serializer.data.get('email'),
                                 confirmation_code=None).exists():
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            confirmation_code = randint(1000, 999999)
            User.objects.filter(username=serializer.data.get('username'),
                                email=serializer.data.get('email'),
                                confirmation_code=None).update(
                                    confirmation_code=confirmation_code)
            send_mail(
                'Письмо с кодом верификации',
                f'Код: {confirmation_code}',
                'from@example.com',
                [serializer.data.get('email')]
            )
            return Response(data=serializer.data, status=HTTP_200_OK)
        return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserGetToken(APIView):
    """Получить токен для зарегистрированного юзера"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserGetTokenSerializer(data=request.data)

        if serializer.is_valid():
            confirmation_code = serializer.data.get('confirmation_code')
            username = serializer.data.get('username')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response('User is not found', status=HTTP_404_NOT_FOUND)
            if User.objects.filter(
                username=username,
                confirmation_code=confirmation_code
            ).exists():
                token = RefreshToken.for_user(user)
                result = {
                    'access': str(token.access_token)
                }
                return Response(data=result, status=HTTP_200_OK)
            return Response('Confirmation code is not correct',
                            status=HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Взаимодействие с эндпоинтом users/"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class UserProfileView(APIView):
    """Взаимодействие с эндпоинтом users/me/. Получение(GET)
    информации о себе и частичное обновление(PATCH) информации о себе"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data,
                                    partial=True)
        if serializer.is_valid():
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class CategoryViewSet(CreateModelMixin,
                      DestroyModelMixin,
                      ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
            self.permission_classes = (AdminOnly,)
        return super().get_permissions()


class GenreViewSet(CreateModelMixin,
                   DestroyModelMixin,
                   ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = ()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
            self.permission_classes = (AdminOnly,)
        return super().get_permissions()


class TitlesViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CommentPagination
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    pagination_class = CommentPagination
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminOrAuthorOrReadOnly)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    pagination_class = CommentPagination
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminOrAuthorOrReadOnly)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            review = title.reviews.get(id=self.kwargs.get('review_id'))
        except TypeError:
            TypeError('У произведения нет такого отзыва')
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            review = title.reviews.get(id=self.kwargs.get('review_id'))
        except TypeError:
            TypeError('У произведения нет такого отзыва')
        serializer.save(author=self.request.user, review=review)
