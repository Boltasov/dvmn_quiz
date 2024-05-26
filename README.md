# Публикация комиксов

Программа предназначена для публикации комиксов с сайта https://xkcd.com/ в группе Вконтакте. При запуске программа произвольно публикует один из комиксов с указанного сайта.

### Как установить

Должны быть предустановлены Python 3 и pip.

Скачайте код с помощью команды в командной строке
```
git clone https://github.com/Boltasov/devman_comic
```
Установите необходимые библиотеки командой
```
python pip install -r requirements.txt
```
Подготовьте ключи

Для Телеграм:
- Получите токен вашего Телеграм-бота (https://botifi.me/ru/help/telegram-existed-bot/)

Для ВКонтакте:
- Получите access_token ВКонтакте (https://dvmn.org/encyclopedia/qna/63/kak-poluchit-token-polzovatelja-dlja-vkontakte/)

Для redis (обязательно):
- Создайте базу данных redis и скопируйте соответствующие значения (https://redislabs.com/)
  - host (пример: redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com)
  - port (пример: 16635)
  - username
  - password

Создайте в той же папке, где находится `main.py` новый файл с названием `.env`. Вставьте в него следующие данные:
```
TG_TOKEN='YOUR_TELEGRAM_TOKEN'
REDIS_HOST='YOUR_REDIS_HOST'
REDIS_PORT='YOUR_REDIS_PORT'
REDIS_USERNAME='YOUR_REDIS_DB_USER_NAME'
REDIS_PASSWORD='YOUR_REDIS_DB_USER_PASSWORD'
VK_ACCESS_TOKEN='YOUR_VK_TOKEN'
QUIZ_DIR='YOUR_QUESTIONS_DIRECTORY'
```

### Запуск
Теперь, чтобы запустить Телеграм-бот, используйте команду:
```commandline
python tg_bot.py
```

Чтобы запустить Телеграм-бот, используйте команду:
```commandline
python vk_bot.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).