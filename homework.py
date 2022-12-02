from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
import os
import time
import logging
from telegram import Bot

from exceptions import HTTPStatusError, TokenError, ErrorFromAPI

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


def check_tokens() -> bool:
    """Проверяем наличие обязательных ключей доступа."""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logger.critical('Нет необходимого токена')
        return False


def send_message(bot: Bot, message: str) -> any:
    """Отправляем сообщение в зависимости от статуса работы."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                         text=message,)
    except Exception as err:
        logger.error(f'Что то пошло не так при отправке сообщения'
                     f'"{message}",{err}', exc_info=True)
    finally:
        logger.debug(f'Сообщение "{message}" отправлено успешно!')


def get_api_answer(timestamp: int) -> dict:
    """Функция делает запрос к эндпоинту API-сервиса и возвращает ответ API."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        raise HTTPStatusError('Ошибка при обращении к API')
    return response.json()


def check_response(response: dict) -> dict:
    """Проверяем значения в ответе API с данными нашей домашней работы."""
    if not isinstance(response, dict):
        raise TypeError('Запрашиваемый ответ не является словарем')
    if 'homeworks' not in response.keys():
        raise TypeError('Нет необходимого ключа "homeworks"')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Ключ "homeworks" не содержит необходимого списка')
    return response.get('homeworks')[0]


def parse_status(homework: dict) -> str:
    """Извлекаем статус конкретной домашней работы."""
    if 'status' not in homework.keys():
        raise ErrorFromAPI(
            ('Отсутствует ключ "status", проверьте выходные данные'))
    if 'homework_name' not in homework.keys():
        raise ErrorFromAPI(
            ('Отсутствует ключ "homework_name", проверьте выходные данные'))
    if homework.get('status') not in HOMEWORK_VERDICTS.keys() or None:
        raise ErrorFromAPI('Неизвестный статус домашней работы')

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
    check_tokens()
    if check_tokens() is False:
        raise TokenError('Отсутствует обязательная переменная окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_message = None

    while True:
        try:
            response = get_api_answer(timestamp - UNIX_MONTH)
            homework = check_response(response)
            message = parse_status(homework)
        except Exception as err:
            logger.error(f'Ошибка при запросе к основному API: {err}')
            message = f'Сбой в работе программы: {err}'
            bot.send_message(
                TELEGRAM_CHAT_ID,
                f'Ошибка при запросе к основному API: {err}'
            )
        if old_message != message:
            send_message(bot, message)
        old_message = message
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
