# Homework Bot - Бот для проверки статуса домашней работы

Простой бот работающий с API Яндекс.Практикум, весь функцианал это отображать статсу проверки кода ревью вашей работы.

Каждые 10 минут бот проверяет API Яндекс.Практикум. И присылает в телеграм статус.
Если работа проверена вы получите сообщение о статусе вашего код ревью.

У API Практикум.Домашка есть лишь один эндпоинт: 

https://practicum.yandex.ru/api/user_api/homework_statuses/

и доступ к нему возможен только по токену.

Получить токен можно по [адресу](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a).

### Принцип работы API
Когда ревьюер проверяет вашу домашнюю работу, он присваивает ей один из статусов:

- работа принята на проверку
- работа возвращена для исправления ошибок
- работа принята

### Запуск на ПК

Клонируем проект:

```bash
git clone https://github.com/Sobodazh/homework_bot.git
```

или

```bash
git clone git@github.com:Sobodazh/homework_bot.git
```

Переходим в папку с ботом.

```bash
cd homework_bot
```

Устанавливаем виртуальное окружение

```bash
python -m venv venv
```

Активируем виртуальное окружение

```bash
source venv/Scripts/activate
```

> Для деактивации виртуального окружения выполянем (после работы)
> ```bash
> deactivate
> ```

Устанавливаем зависимости

```bash
pip install -r requirements.txt
```

В консолb импортируем токены для Яндекс Практикум и для Телеграмм:

```bash
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID>
```

Запускаем бота

```bash
python homework.py
```

Бот будет работать, и каждые 10 минут проверять статус вашей домашней работы.
