## API_YAMDB

![workflow](https://github.com/Timoha23/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Описание
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором.
## Использованные технологии

* Python 3.9;
* Django 2.2.16;
* Django REST Framework 3.12.4;
* Simple JWT 4.7.2.
* Docker;
* PostgreSQL.

## 1. Запуск проекта:

 Клонирование проекта:
 

    git clone https://github.com/Timoha23/yamdb_final.git
Переход в директорию с docker-compose:

    cd yamdb_final/infra

Подъем контейнеров:

    docker-compose up -d --build

Выполняем миграции:

    docker-compose exec web python manage.py migrate

Собираем статику:

    docker-compose exec web python manage.py collectstatic --no-input

Создаем суперпользователя:

    docker-compose exec web python manage.py createsuperuser

## 2. Заполнение базы данных проекта:
Имея логин и пароль, созданного нами ранее, суперюзера, переходим по следующей ссылке: http://localhost/admin/, авторизовываемся и вносим нужные записи в базу данных.
Для создания резервной копии (дампа) базы данных используем следующую команду:

    docker-compose exec web python manage.py dumpdata > fixtures.json
## 3. Остановка и запуск контейнеров:
Остановка:

    docker-compose stop

Запуск:

    docker-compose start

## 4. Шаблон наполнения .env:

    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432

**Автор:**
*Ершов Тимофей Сергеевич*
