from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
import os
import time
import logging

from exceptions import HTTPStatusError

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
UNIX_MONTH = 2629743
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяем наличие обязательных ключей доступа."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    return False


def send_message(bot, message):
    """Отправляем сообщение в зависимости от статуса работы."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                         text=message,)
        logger.debug(f'Сообщение "{message}" отправлено успешно!')
    except Exception as err:
        logger.error(f'Что то пошло не так при отправке сообщения'
                     f'"{message}",{err}', exc_info=True)


def get_api_answer(timestamp):
    """Функция делает запрос к эндпоинту API-сервиса и возвращает ответ API."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != HTTPStatus.OK:
            raise HTTPStatusError('Ошибка при обращении к API')
    except requests.RequestException as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        telegram.Bot(token=TELEGRAM_TOKEN).send_message(
            TELEGRAM_CHAT_ID,
            f'Ошибка при запросе к основному API: {error}'
        )
    return response.json()


def check_response(response):
    """Проверяем значения в ответе API с данными нашей домашней работы."""
    if not isinstance(response, dict):
        raise TypeError('Запрашиваемый ответ не является словарем')
    if 'homeworks' not in response.keys():
        raise TypeError('Нет необходимого ключа "homeworks"')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Ключ "homeworks" не содержит необходимого списка')
    return response.get('homeworks')[0]


def parse_status(homework):
    """Извлекаем статус конкретной домашней работы."""
    if 'status' not in homework.keys():
        raise KeyError('Нет необходимого ключа статуса домашней работы')
    if 'homework_name' not in homework.keys():
        raise KeyError('Нет необходимого ключа названия домашней работы')
    if homework.get('status') not in HOMEWORK_VERDICTS.keys() or None:
        raise KeyError('Неизвестный статус домашней')

    verdict = homework.get('status')
    homework_name = homework.get('homework_name')
    message = HOMEWORK_VERDICTS[verdict]

    return (
        f'Изменился статус проверки работы "'
        f'{homework_name}", '
        f'{verdict}. '
        f' {message}'
    )


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        raise logger.critical('Отсутствует обязательная переменная окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_message = None

    while True:
        try:
            response = get_api_answer(timestamp - UNIX_MONTH)
            homework = check_response(response)
            message = parse_status(homework)
        except Exception as err:
            message = f'Сбой в работе программы: {err}'

        if old_message != message:
            send_message(bot, message)
        old_message = message
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
