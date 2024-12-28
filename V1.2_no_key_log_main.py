from datetime import datetime, timezone
import requests
import json
import logging
from utils.signature import generate_signature

# Налаштування логування
logging.basicConfig(filename='log.txt', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s')

# Читання конфігураційного файлу
try:
    with open('config.json', 'r') as file:
        config = json.load(file)
except Exception as e:
    logging.error(f"Помилка при читанні config.json: {str(e)}")
    raise

# Читання API ключів
try:
    with open('api_keys.json', 'r') as file:
        api_keys = json.load(file)
except Exception as e:
    logging.error(f"Помилка при читанні api_keys.json: {str(e)}")
    raise

# Функція для виведення коштів
def withdraw(amount, address, config, api_keys):
    url = '/api/v5/asset/withdrawal'
    base_url = 'https://www.okx.com'
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = 'POST'
    body = {
        'currency': config["currency"],
        'amount': amount,
        'destination': '4',  # 4 - адреса гаманця
        'toAddress': address,
        'chain': config["chain"],
        'pwd': api_keys["withdrawal_password"]
    }

    signature = generate_signature(timestamp, method, url, json.dumps(body), api_keys['secret_key'])
    headers = {
        'OK-ACCESS-KEY': api_keys["api_key"],
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': api_keys["passphrase"],
        'Content-Type': 'application/json'
    }
    
    # Вивід параметрів запиту для діагностики без чутливих даних
    logging.debug(f"URL: {base_url + url}")
    logging.debug(f"Headers: {{'OK-ACCESS-KEY': '***', 'OK-ACCESS-SIGN': '***', 'OK-ACCESS-TIMESTAMP': {timestamp}, 'OK-ACCESS-PASSPHRASE': '***', 'Content-Type': 'application/json'}}")
    logging.debug(f"Body: {{'currency': {config['currency']}, 'amount': {amount}, 'destination': '4', 'toAddress': {address}, 'chain': {config['chain']}, 'pwd': '***'}}")
    
    try:
        response = requests.post(base_url + url, headers=headers, json=body)
        response.raise_for_status()
        logging.info(f"Успішне виведення {amount} {config['currency']} на адресу {address}")
        print(f"Успішне виведення {amount} {config['currency']} на адресу {address}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Помилка при виведенні: {str(e)}")
        print(f"Помилка при виведенні: {str(e)}")

# Функція для друку параметрів конфігурації
def print_config():
    print(json.dumps(config, indent=4))

# Основна логіка
def main():
    print_config()
    
    # Приклад виклику функції withdraw з тестовими даними (замініть на реальні дані)
    test_amount = "0.0001"
    test_address = "0xd5DE0DeaDF2F5ED35Ee388D8162060BDBE76e816"
    withdraw(test_amount, test_address, config, api_keys)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Непередбачена помилка: {str(e)}")
        print(f"Непередбачена помилка: {str(e)}")
