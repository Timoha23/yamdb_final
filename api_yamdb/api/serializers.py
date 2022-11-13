from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from reviews.models import Comment, Review
from title.models import Category, Genre, Title
from users.models import User


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, data):
        if data == 'me':
            raise serializers.ValidationError('Имя "me" нельзя использовать в'
                                              ' качестве username')
        return data


class UserGetTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class CategorySerializer(ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class TitleSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleCreateSerializer(ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewsSerializer(serializers.ModelSerializer):
    """Отзывы на произведения"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ['title']

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title_id = (
                self.context['request'].parser_context['kwargs']['title_id']
            )
            author = self.context['request'].user
            if Review.objects.filter(title_id=title_id,
                                     author=author).exists():
                raise serializers.ValidationError(
                    'Нельзя оставить отзыв на одно произведение дважды'
                )
        return data

    def validate_score(self, value):
        if 0 >= value > 10:
            raise serializers.ValidationError('Оценка должная быть от 1 до 10')
        return value


class CommentsSerializer(serializers.ModelSerializer):
    """Комментарии к отзывам"""

    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        fields = '__all__'
        read_only_fields = ['review']
        model = Comment
