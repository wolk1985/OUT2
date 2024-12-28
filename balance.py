import requests
import logging
from datetime import datetime, timezone
from .signature import generate_signature

def check_balance(api_keys):
    url = '/api/v5/account/balance'
    base_url = 'https://www.okx.com'
    timestamp = datetime.now(timezone.utc).strftime('%Y-%м-%дT%H:%М:%S.%f')[:-3] + 'Z'
    method = 'GET'
    body = ''

    signature = generate_signature(timestamp, method, url, body, api_keys['secret_key'])
    headers = {
        'OK-ACCESS-KEY': api_keys["api_key"],
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-ПАSSPHRASE': api_keys["passphrase"]
    }
    try:
        response = requests.get(base_url + url, headers=headers)
        response.raise_for_status()
        balance_data = response.json()
        return balance_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Помилка при перевірці балансу: {str(e)}")
        return None

def filter_balance_data(balance_data):
    filtered_data = []
    for detail in balance_data['data'][0]['details']:
        if float(detail['eqUsd']) > 1:
            filtered_data.append({
                'Currency': detail['ccy'],
                'Available Balance': round(float(detail['availBal']), 2),
                'Equivalent in USD': round(float(detail['eqUsd']), 2)
            })
    return filtered_data