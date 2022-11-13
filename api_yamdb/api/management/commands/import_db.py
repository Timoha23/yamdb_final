from csv import DictReader

from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):

    def handle(self, *args, **options):
        for record in DictReader(open('./static/data/category.csv',
                                 encoding='utf-8')):
            category = Category(id=record['id'],
                                name=record['name'],
                                slug=record['slug'])
            category.save()

        for record in DictReader(open('./static/data/genre.csv',
                                 encoding='utf-8')):
            genre = Genre(id=record['id'],
                          name=record['name'],
                          slug=record['slug'])
            genre.save()

        for record in DictReader(open('./static/data/users.csv',
                                 encoding='utf-8')):
            user = User(id=record['id'],
                        username=record['username'],
                        email=record['email'],
                        role=record['role'],
                        bio=record['bio'],
                        first_name=record['first_name'],
                        last_name=record['last_name'])
            user.save()

        for record in DictReader(open('./static/data/titles.csv',
                                 encoding='utf-8')):
            title = Title(id=record['id'],
                          name=record['name'],
                          year=record['year'],
                          category=Category.objects.get(id=record['category']))
            title.save()

        for record in DictReader(open('./static/data/review.csv',
                                 encoding='utf-8')):
            review = Review(id=record['id'],
                            title=Title.objects.get(id=record['title_id']),
                            text=record['text'],
                            author=User.objects.get(id=record['author']),
                            score=record['score'],
                            pub_date=record['pub_date'])
            review.save()

        for record in DictReader(open('./static/data/comments.csv',
                                 encoding='utf-8')):
            comment = Comment(
                id=record['id'],
                review=Review.objects.get(id=record['review_id']),
                text=record['text'],
                author=User.objects.get(id=record['author']),
                pub_date=record['pub_date'])
            comment.save()
