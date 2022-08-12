import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
import telegram.error
from dotenv import load_dotenv

import exceptions

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'bot_logger.log',
    maxBytes=50000000,
    backupCount=3
)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 60
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в телеграм чат."""
    logger.info('Попытка отправки сообщения')
    chat_id = TELEGRAM_CHAT_ID
    text = message
    try:
        bot.send_message(chat_id=chat_id, text=text)
        logger.info('Сообщение отправленно')
    except telegram.error.TelegramError:
        raise exceptions.SendMessageError('Ошибка отправки сообщения')


def get_api_answer(current_timestamp: time) -> dict:
    """Делает запрос к API Яндекс.Практикума."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    logger.info('Делаю запрос к API')
    try:
        homework_statuses = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params=params
        )
        logger.info('Запрос сделал')
    except requests.exceptions.RequestException as error:
        text_error = f'Сбой при запросе к эндпоинту: {error}'
        raise exceptions.AccessApiError(text_error)
    if homework_statuses.status_code != 200:
        text_error = f'Ошибка {homework_statuses.status_code}. Эндпоинт не доступен.'
        raise exceptions.StatusResponseNotOKError(text_error)
    response = homework_statuses.json()
    return response


def check_response(response: dict) -> dict:
    """Проверяет API на корректность."""
    if type(response) is not dict:
        raise exceptions.TypeIsNotDictError(
            'В check_response передан не словарь'
        )
    try:
        homework = response['homeworks']
    except KeyError as error:
        raise exceptions.MissingExpectedKeysError(
            f'Отсутствие ожидаемых ключей в ответе API. Ошибка {error}',
        )
    if type(homework) is not list:
        raise exceptions.TypeIsNotListError(
            'В полученном словаре нет списка домашнийх работ'
        )
    try:
        homework[0]
    except IndexError:
        return dict()
    return homework[0]


def parse_status(homework: dict) -> str:
    """Извлекает информацию о статусе домашней работы."""
    if 'homework_name' not in homework:
        raise exceptions.KeyAcquisitionError(
            'Ошибка получения ключа "homework_name"'
        )
    homework_name = homework.get('homework_name')
    if 'status' not in homework:
        raise exceptions.KeyAcquisitionError(
            'Ошибка получения ключа "status"'
        )
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_text = 'Нет необходимых токенов для продолжения работы.'
        send_message(bot, error_text)
        logger.critical(error_text)
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    message_error = ''
    last_message = ''
    last_response = {}
    while True:
        try:
            response = get_api_answer(current_timestamp)
            checking_response = check_response(response)
            if last_response != checking_response:
                last_response = checking_response
                if checking_response:
                    status = parse_status(checking_response)
                    send_message(bot, status)

            text = 'Работа пока что не проверенна.'
            if text != last_message:
                last_message = text
                send_message(bot, text)

        except Exception as error:
            error_text = f'Ошибка: {error}'
            logger.error(error_text, exc_info=True)
            if error_text != message_error:
                message_error = error_text
                send_message(bot, error_text)

        else:
            logger.info('Все хорошо. Итерация выполнена.')

        finally:
            logger.info(f'Сплю на {RETRY_TIME / 60} минут')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
