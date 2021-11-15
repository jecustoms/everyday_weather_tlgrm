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

URL = 'https://api.weather.yandex.ru/v2/informers/'


class CustomsError(Exception):
    pass


def good_morning():
    current_datetime = datetime.now()
    message = (
        f'Доброе утро! Сегодня {current_datetime.day} '
        f'{months[current_datetime.month]} {current_datetime.year} года.'
    )
    return message


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
    return message + '\n'


def sunset_sunrise_time(weather_request):
    logger.debug('Парсинг восхода и заката')
    weather_object = weather_request.get('forecast')
    sunrise = weather_object.get('sunrise')
    sunset = weather_object.get('sunset')
    message = (
        f'Восход: {sunrise}\nЗакат: {sunset}'
    )
    return message + '\n'


def day_evening_forecast(weather_request):
    logger.debug('Парсинг прогноза погода днем и вечером')
    weather_object = weather_request.get('forecast')
    day_object = weather_object.get('parts')[0]
    temperature = day_object.get('temp_avg')
    feels_like = day_object.get('feels_like')
    condition = weather_conditions[day_object.get('condition')]
    day_message = (
        f'Днем будет {condition}, температура {temperature} '
        f'°C. По ощущениям как {feels_like} °C.'
    )
    evening_object = weather_object.get('parts')[1]
    temperature = evening_object.get('temp_avg')
    feels_like = evening_object.get('feels_like')
    condition = weather_conditions[evening_object.get('condition')]
    evening_message = (
        f'Вечером будет {condition}, температура {temperature} '
        f'°C. По ощущениям как {feels_like} °C.'
    )
    return day_message + evening_message + '\n'


def generate_message(weather, hour):
    if hour <= 12:
        text = (
            good_morning() + current_weather_obj_parser(weather)
            + sunset_sunrise_time(weather)
            + day_evening_forecast(weather)
        )
    else:
        text = 'Добрый вечер!' + current_weather_obj_parser(weather)
    return text


def get_weather_and_make_message(hour):
    weather = get_weather()
    message = generate_message(weather, hour)
    return message


def main():
    logger.debug('Запуск бота')
    bot_client = telegram.Bot(TELEGRAM_TOKEN)
    while True:
        dt = datetime.now().timetuple()
        hour, minute = dt[3], dt[4]
        weekday = datetime.now().weekday()
        try:
            if 0 <= weekday <= 4 and hour == 5 and (0 <= minute <= 20):
                send_message(get_weather_and_make_message(hour), bot_client)
            elif 5 <= weekday <= 6 and hour == 7 and (0 <= minute <= 20):
                send_message(get_weather_and_make_message(hour), bot_client)
            elif hour == 16 and (0 <= minute <= 20):
                send_message(get_weather_and_make_message(hour), bot_client)
            requests.get('http://yandex.ru')
            time.sleep(1200)
        except Exception as error:
            logger.error(error, exc_info=True)
            send_message(f'Бот столкнулся с ошибкой {error}', bot_client)
            time.sleep(100)
    logger.debug('Отсановка бота')


if __name__ == '__main__':
    main()
