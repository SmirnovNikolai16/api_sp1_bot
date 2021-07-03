import json
import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HOMEWORK_STATUS = {
    'reviewing': 'Работа взята в ревью.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'rejected': 'К сожалению, в работе нашлись ошибки.'
}
TIMER = 20

logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

bot = telegram.Bot(token=f'{TELEGRAM_TOKEN}')


class NegativeValueException(ValueError):
    pass


def parse_homework_status(homework):
    try:

        if 'homework_name' not in homework:
            raise NegativeValueException('Не найдено имя домашней работы!')
        if 'status' not in homework:
            raise NegativeValueException('Не найден статус домашней работы!')

        homework_name = homework.get('homework_name')
        status = homework.get('status')

        if status not in HOMEWORK_STATUS:
            raise NegativeValueException(
                f'Домашняя работа вернулась с неизвестным статусом {status}'
            )

        verdict = HOMEWORK_STATUS[status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'

    except NegativeValueException as e:
        logging.exception(f'Получена некорректная информация: {e}')
        raise


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        logging.exception(f'Возникла ошибка {e} при соединении с сервером')
        raise
    except json.decoder.JSONDecodeError:
        logging.exception('Возникла ошибка при распаковке JSON')
        raise


def send_message(message):
    logging.info('Сообщение отправлено')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.info('Бот запущен')
    while True:
        try:
            try:
                current_timestamp = int(time.time())
                homework = get_homeworks(current_timestamp)
                if homework.get('homeworks'):
                    message = parse_homework_status(homework['homeworks'][0])
                    send_message(message)
                time.sleep(TIMER)

            except Exception as e:
                logging.exception(f'Бот упал с ошибкой: {e}')
                send_message(f'Бот упал с ошибкой: {e}')
                time.sleep(TIMER)
                continue
        except KeyboardInterrupt:
            break
    logging.info('Бот отключён')


if __name__ == '__main__':
    main()
