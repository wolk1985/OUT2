from datetime import datetime, timezone
import requests
import json
import time
import logging
from utils.signature import generate_signature
from utils.balance import check_balance, filter_balance_data
from utils.gwei import check_gwei
from utils.wallet import load_wallet_addresses

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

# Читання адрес із файлу CSV
try:
    wallet_addresses = load_wallet_addresses('wallets.csv')
except Exception as e:
    logging.error(f"Помилка при читанні wallets.csv: {str(e)}")
    raise

# Функція для виведення коштів
def withdraw(address, config, api_keys):
    url = '/api/v5/asset/withdrawal'
    base_url = 'https://www.okx.com'
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = 'POST'
    body = {
        'currency': config["currency"],
        'amount': config["amount"],
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
    logging.debug(f"Headers: {{'OK-ACCESS-KEY': '***', 'OK-ACCESS-SIGN': '***', 'OK-ACCESS-TIMESTAMP': {timestamp}, 'OK-ACCESS-PASСПHRASE': '***', 'Content-Type': 'application/json'}}")
    logging.debug(f"Body: {{'currency': {config['currency']}, 'amount': {config['amount']}, 'destination': '4', 'toAddress': '***', 'chain': {config['chain']}, 'pwd': '***'}}")
    
    try:
        response = requests.post(base_url + url, headers=headers, json=body)
        response.raise_for_status()
        logging.info(f"Успішне виведення {config['amount']} {config['currency']} на адресу {address}")
        print(f"Успішне виведення {config['amount']} {config['currency']} на адресу {address}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Помилка при виведенні: {str(e)}")
        print(f"Помилка при виведенні: {str(e)}")

# Функція для друку параметрів конфігурації
def print_config():
    print(json.dumps(config, indent=4))

# Основна логіка
def main():
    print_config()
    
    # Перевірка значення GWEI
    if check_gwei(config, api_keys):
        # Отримання балансу
        balance = check_balance(api_keys)
        if balance:
            filtered_balance = filter_balance_data(balance)
            # Вивід балансу та еквіваленту в USD
            for entry in filtered_balance:
                print(f"Currency: {entry['Currency']}, Available Balance: {entry['Available Balance']}, Equivalent in USD: {entry['Equivalent in USD']}")
            total_eq_usd = round(float(balance['data'][0]['totalEq']), 2)
            print(f"Total Equivalent in USD: {total_eq_usd}")

            eth_balance = next((item for item in balance['data'][0]['details'] if item['ccy'] == 'ETH'), None)
            if eth_balance and float(eth_balance['availBal']) >= float(config["amount"]):
                # Виклик функції withdraw для кожної адреси з файлу wallets.csv
                for address in wallet_addresses:
                    withdraw(address, config, api_keys)
            else:
                print("Недостатньо коштів на балансі")
        else:
            print("Не вдалося отримати баланс")
    else:
        print("Виведення коштів заборонено через високе значення GWEI")

    # Чекати підтвердження від користувача перед закриттям скрипта
    input("Натисніть Enter, щоб завершити роботу скрипта...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Непередбачена помилка: {str(e)}")
        print(f"Непередбачена помилка: {str(e)}")
