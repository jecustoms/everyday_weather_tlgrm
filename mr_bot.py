import logging
import os
import requests
import telegram
import time

from datetime import datetime
from dotenv import load_dotenv

from dictionaries import weather_conditions, months


logging.basicConfig(
    level=logging.DEBUG, filename='telegram_bot.log',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TOKEN = os.getenv('TOKEN')

URL = 'https://api.weather.yandex.ru/v2/forecast'


class CustomsError(Exception):
    pass


def good_morning():
    current_datetime = datetime.now()
    message = (
        f'Доброе утро! Сегодня {current_datetime.day} '
        f'{months[current_datetime.month]} {current_datetime.year} года.'
    )
    return message + '\n\n'


def get_weather():
    logger.debug('Погода запрошена')
    headers = {'X-Yandex-API-Key': TOKEN}
    params = {'lat': '55.794249', 'lon': '37.404034'}  # lat and lon for Moscow
    try:
        response = requests.get(URL, params=params, headers=headers)
        return response.json()
    except requests.RequestException as error:
        raise CustomsError(f'URL недоступен - ошибка: {error}')


def send_message(message, bot_client):
    logger.info(f'Отрпавлено сообщение: {message}')
    return bot_client.send_message(CHAT_ID, message)


def current_weather_obj_parser(weather_request):
    logger.debug('Парсинг текущей погоды')
    weather_object = weather_request.get('fact')
    temperature = weather_object.get('temp')
    feels_like = weather_object.get('feels_like')
    condition = weather_conditions[weather_object.get('condition')]
    water_temp = weather_object.get('temp_water')
    message = (
        f'Сейчас {condition} и температура на улице составляет {temperature} '
        f'°C, что ощущается как {feels_like} °C.'
    )
    if water_temp is not None:
        message += 'Температура воды: {water_temp}'
    return message + '\n\n'


def sunset_sunrise_time(weather_request):
    logger.debug('Парсинг восхода и заката')
    weather_object = weather_request.get('forecasts')
    sunrise = weather_object[0].get('sunrise')
    sunset = weather_object[0].get('sunset')
    message = (
        f'Восход: {sunrise}\nЗакат: {sunset}'
    )
    return message + '\n\n'


def day_evening_forecast(weather_request):
    logger.debug('Парсинг прогноза погода днем и вечером')
    weather_object = weather_request.get('forecasts')
    day_object = weather_object[0].get('parts')['day']
    temperature = day_object.get('temp_avg')
    feels_like = day_object.get('feels_like')
    condition = weather_conditions[day_object.get('condition')]
    day_message = (
        f'Днем ожидается {condition}, температура {temperature} '
        f'°C. Будет ощущаться как {feels_like} °C.'
    )
    evening_object = weather_object[0].get('parts')['evening']
    temperature = evening_object.get('temp_avg')
    feels_like = evening_object.get('feels_like')
    condition = weather_conditions[evening_object.get('condition')]
    evening_message = (
        f'Вечером ожидается {condition}, температура {temperature} '
        f'°C. Будет ощущаться как {feels_like} °C.'
    )
    return day_message + '\n\n' + evening_message + '\n\n'


def random_func_name_get_current_time(weather_request):  # new name needed -_-
    logger.debug('Получаем текущее время сервера')
    server_time = weather_request.get('now_dt')
    hour = server_time[11:13]
    minute = server_time[14:16]
    return hour, minute


def main():
    logger.debug('Запуск бота')
    bot_client = telegram.Bot(TELEGRAM_TOKEN)
    while True:
        try:
            weather = get_weather()
            hour, minute = random_func_name_get_current_time(weather)
            weekday = datetime.now().weekday()
            if weather:
                text = (
                    good_morning() + current_weather_obj_parser(weather)
                    + sunset_sunrise_time(weather)
                    + day_evening_forecast(weather)
                )
                if 0 <= weekday <= 4 and (
                    hour == '05' and (0 <= int(minute) <= 20)
                ):
                    send_message(text, bot_client)
                elif 5 <= weekday <= 6 and (
                    hour == '07' and (0 <= int(minute) <= 20)
                ):
                    send_message(text, bot_client)
            time.sleep(1200)  # запрос раз в 20 минут
        except Exception as error:
            logger.error(error, exc_info=True)
            send_message(f'Бот столкнулся с ошибкой {error}', bot_client)
            time.sleep(50)
    logger.debug('Отсановка бота')


if __name__ == '__main__':
    main()
