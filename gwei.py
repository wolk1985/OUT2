import requests
import logging

def get_current_gwei(api_keys):
    url = f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={api_keys["etherscan_api_key"]}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['status'] == '1':
            return round(float(data['result']['ProposeGasPrice']), 2)
        else:
            logging.error(f"Помилка при запиті до Etherscan: {data['message']}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Помилка при запиті до Etherscan: {str(e)}")
        return None

def check_gwei(config, api_keys):
    gwei = get_current_gwei(api_keys)
    if gwei is not None:
        config_max_gwei = config.get('max_gwei', 5)  # Використовується 5 як значення за замовчуванням, якщо max_gwei відсутній

        if gwei < config_max_gwei:
            logging.info(f"Поточне значення GWEI ({gwei}) менше {config_max_gwei}, виконання зняття коштів дозволено.")
            return True
        else:
            logging.warning(f"Поточне значення GWEI ({gwei}) більше {config_max_gwei}, виведення коштів заборонено.")
    else:
        logging.error("Не вдалося отримати поточне значення GWEI")
    return False