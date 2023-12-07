## Проект «Foodgram»
***
[![base_workflow](https://github.com/VorVorsky/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/VorVorsky/foodgram-project-react/actions/workflows/foodgram_workflow.yml)<br/>
***
Временно отключен сервер.<br/>
[Ссылка на сайт](https://klaxonvs.ddns.net/recipes)
[Ссылка на API](https://klaxonvs.ddns.net/api/)
[Ссылка на админку](https://klaxonvs.ddns.net/admin/)
[Ссылка на redoc](https://klaxonvs.ddns.net/api/docs/)

***
### Технологии:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
***
### Описание:
Cайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
***

## Запуск проекта через Doker:

1. Клонировать репозиторий: <br/>``git clone git@github.com:VorVorsky/foodgram-project-react.git``
2. Создать файл **.env**

### Образец .env файла -- секретные переменные для проекта расположить в папке<br/>
``infra/``:
* SECRET_KEY (ключ Django-проекта)
* ALLOWED_HOSTS (хосты разделённые "|")
* LOCAL (для локального запуска на компьютере)
* DEBUG (режим отладки)
* DB_ENGINE (используемая база, по умолчанию django.db.backends.postgresql)
* POSTGRES_DB (имя базы)
* POSTGRES_USER (пользователь базы)
* POSTGRES_PASSWORD (пароль пользователя)
* DB_HOST (хост)
* DB_PORT (порт)
* SQLITE (sqlite как бд)

3. В консоли из папки `infra/` соберите контейнер: `docker compose up -d --build`
4. Выполнить миграции:
   * `docker compose exec backend python manage.py makemigrations [module]`,
   * `docker compose exec backend python manage.py migrate`
5. Соберите статику:<br/>
`docker compose exec backend python manage.py collectstatic --no-input`

### Если необходима выгрузка данных в БД из csv файлов:
1. Выполнить выгрузку ингредиентов и базовых тегов коммандой:<br/>`docker compose exec backend python manage.py load_data`
2. В PostgreSQL В связи с загрузкой могут сбиться данные о последнем индексе, необходимо<br/>
получить SQL команды для их обновления:<br/>`docker compose exec backend python manage.py sqlsequencereset recipes > sql_reset.txt`
3. Войти в оболочку psql: `docker compose exec db psql -U ${POSTGRES_USER} ${POSTGRES_DB}`
4. Выполните полученные SQL запросы.

### Создание суперпользователя:
* Используйте команду: `docker compose exec backend python manage.py createsuperuser`
#### Если возникает ошибка:
`Superuser creation skipped due to not running in a TTY.`<br/>
`You can run manage.py createsuperuser in your project to create one manually.`<br/>
* Используйте команду: `winpty docker-compose exec backend python manage.py createsuperuser`
