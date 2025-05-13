import requests
from flask import current_app
from functools import lru_cache


@lru_cache(maxsize=32, ttl=3600)  # Кэш на 1 час
def convert_currency(amount, from_currency, to_currency):
    """Конвертация валют через внешний API"""
    try:
        api_key = current_app.config['CURRENCY_API_KEY']
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, params={'access_key': api_key})
        rates = response.json()['rates']
        return amount * rates[to_currency]
    except Exception as e:
        current_app.logger.error(f'Currency conversion error: {str(e)}')
        return amount  # Возвращаем исходную сумму при ошибке
