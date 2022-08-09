import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

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

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в телеграм чат."""
    chat_id = TELEGRAM_CHAT_ID
    text = message
    try:
        bot.send_message(chat_id=chat_id, text=text)
        logger.info('Сообщение отправлено')
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения: {error}', exc_info=True)


def get_api_answer(current_timestamp: time) -> dict:
    """Делает запрос к API Яндекс.Практикума."""
    timestamp = current_timestamp or int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=headers,
            params=params
        )
    except Exception as error:
        logger.error(f'Ошибка {error} при запросе к API.')
        raise Exception(f'Ошибка {error} при запросе к API.')
    if homework_statuses.status_code != 200:
        logger.error(
            f'Ошибка {homework_statuses.status_code}. Эндпоинт не доступен.'
        )
        raise Exception(
            f'Ошибка {homework_statuses.status_code}. Эндпоинт не доступен.'
        )
    response = homework_statuses.json()
    return response


def check_response(response: dict) -> dict:
    """Проверяет API на корректность."""
    if type(response) is not dict:
        raise TypeError('В check_response передан не словарь')
    try:
        homework = response['homeworks']
    except KeyError as error:
        logger.error(
            f'Отсутствие ожидаемых ключей в ответе API. Ошибка {error}',
            exc_info=True)
    try:
        homework[0]
    except IndexError as error:
        logger.error(
            f'Список домашних работ пуст {error}'
        )
        raise IndexError(f'Список домашних работ пуст {error}')
    return homework[0]


def parse_status(homework: dict) -> str:
    """Извлекает информацию о статусе домашней работы."""
    if 'homework_name' not in homework:
        logger.error('Ошибка ключа получения "homework_name"')
        raise KeyError('Ошибка ключа получения "homework_name"')
    homework_name = homework.get('homework_name')
    if 'status' not in homework:
        logger.error('Ошибка ключа получения "status"')
        raise KeyError('Ошибка ключа получения "status"')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_response = {}
    while True:
        try:
            if check_tokens():
                response = get_api_answer(current_timestamp)
                if response != last_response:
                    try:
                        checking_response = check_response(response)
                    except IndexError:
                        status = 'Работа еще не посступила на проверку.'
                        send_message(bot, status)
                        current_timestamp = time.time()
                        time.sleep(RETRY_TIME)
                    try:
                        if response != last_response:
                            last_response = response
                            checking_response = check_response(response)
                            status = parse_status(checking_response)
                            send_message(bot, status)
                    except Exception as error:
                        logger.error(
                            f'Что то с отправкой сообщения. {error}',
                            exc_info=True
                        )
        except Exception as error:
            logger.critical(
                f'Отсутствие обязательных переменных окружения {error}', exc_info=True
            )
            logging.critical(
                f'Отсутствие обязательных переменных окружения {error}'
            )
            time.sleep(RETRY_TIME)
        else:
            logging.info('Все хорошо')

if __name__ == '__main__':
    main()
