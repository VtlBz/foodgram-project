# Проект FoodGram

Cервис **FoodGram**, для размещения **рецептов** кулинарных произведений пользователей.


---

### Использованные технологии:

- ***Django** 4.1*
- ***Django REST Framework** 3.14*
- *Библиотека **Djoser** 2.1*
- *Библиотека **Pillow** 9.4*

*Приложение написано на **Python** 3.9*

---

![Статус](https://github.com/VtlBz/foodgram-project-react/actions/workflows/main.yaml/badge.svg)

---

### Как начать работу с проектом:

Клонировать репозиторий и перейти в нём в папку с конфигурацией сборки контейнеров:
```
git clone git@github.com:VtlBz/foodgram-project-react.git
```
```
cd foodgram-project-react/backend/
```

В указанной папке в файле .env указать переменные окружения, соответствующие проекту.
Пример заполнения:
```
SECRET_KEY=<указать-тут-ключ-проекта>
ALLOWED_HOSTS=<перечислить разрешенные хосты через пробел>

DB_ENGINE=django.db.backends.postgresql # по умолчанию работаем с postgresql
DB_NAME=postgres # указать имя базы данных
POSTGRES_USER=<имя_пользователя_бд> # логин для подключения к базе данных
POSTGRES_PASSWORD=<пароль пользователя бд> # пароль для подключения к БД (установите свой)
DB_HOST=fg-db # название сервиса (контейнера), по умолчанию - yamdb-db
DB_PORT=5432 # порт для подключения к БД, стандартный по умолчанию
```

Копировать на сервер папку *docs* и файлы *.env*, *default.conf* и *docker-compose.yaml*:
```
scp -r docs <username>@<server>:/home/<username>
scp .env <username>@<server>:/home/<username>
scp default.conf <username>@<server>:/home/<username>
scp docker-compose.yaml <username>@<server>:/home/<username>

```

В GitHub Actions указать в репозитории все необходимые переменные:
```
DOCKER_PASSWORD # пароль DockerHub, где будет храниться образ основной части проекта
DOCKER_USERNAME # имя пользователя (репозитория) DockerHub
SSH_KEY # ключ, с помощью которого можно подключится к серверу для деплоя
HOST # имя или ардес сервера
USER # логин пользователя на сервере
TELEGRAM_TOKEN # Токен ТГ бота, который сможет выслать оповещение об удачном деплое
TELEGRAM_TO # ID чата (пользователя), которому придёт оповещение
```

При первом запуске создать суперпользователя:
```
docker compose exec fg-srv python manage.py createsuperuser
```

---

### Импорт заранее подготовленных данных б ингридиентах:  
Для импотра данных необходимо, что бы название всех таблиц соответствовало названию моделей, в которые производится импорт из этих таблиц.  
Команда для импорта - ***fill_db***.

  ```
  manage.py fill_db -p <folder_path> # выполнять внутри контейнера
  ```

Аргумент ***-p*** *(**--path**)* опциональный, 
вместо него можно указать путь к папке в переменной **default** в файле recipes/management/commands/fill_db.py.
(указывать путь к папке с файлом, не к самому файлу)

\* *Тестовые данные лежат в папке ./static/ingredients.csv*

[Тестовый сервер ***возможно*** работает тут](http://jstlnk.click/)