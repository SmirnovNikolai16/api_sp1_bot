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

bot = telegram.Bot(token=f'{TELEGRAM_TOKEN}')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    if status != 'approved':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(URL, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)



def main():
    current_timestamp = int(time.time())
    

    while True:
        try:
            logging.basicConfig(
            level=logging.DEBUG,
            filename='bot.log', 
            format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
            )
            homework = get_homeworks(current_timestamp)
            message = parse_homework_status(homework['homeworks'][0])
            logging.info('Send message')
            send_message(message)
            logging.info('Message sent')
            time.sleep(20*60)

        except Exception as e:
            logging.exception(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(20)
            continue


if __name__ == '__main__':
    main()
