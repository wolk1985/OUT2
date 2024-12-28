import json
import time
import logging
from utils.signature import generate_signature
from utils.balance import check_balance, filter_balance_data
from utils.gwei import check_gwei
from utils.wallet import process_wallet_indexes, load_wallet_addresses

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
wallet_addresses = load_wallet_addresses('wallets.csv')

# Функція для виведення коштів
def withdraw(amount, address, config, api_keys):
    url = '/api/v5/asset/withdrawal'
    base_url = 'https://www.okx.com'
    timestamp = datetime.now(timezone.utc).strftime('%Y-%м-%дT%H:%М:%S.%f')[:-3] + 'Z'
    method = 'POST'
    body = {
        'currency': config["currency"],
        'amount': amount,
        'destination': '4',  # 4 - адреса гаманця
        'toAddress': address,
        'chain': config["chain"],
        'fee': config["max_fee"],
        'pwd': api_keys["withdrawal_password"]
    }

    signature = generate_signature(timestamp, method, url, body, api_keys['secret_key'])
    headers = {
        'OK-ACCESS-KEY': api_keys["api_key"],
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-ПАSSPHRASE': api_keys["passphrase"],
        'Content-Type': 'application/json'
    }
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
    while True:
        print_config()
        
        # Вивід адрес гаманців з файлу wallets.csv за порядковими номерами з config.json
        if "wallet_indexes" in config:
            print("Адреси гаманців вибрані з wallets.csv:")
            selected_addresses = []
            processed_indexes = process_wallet_indexes(config["wallet_indexes"])
            for index in processed_indexes:
                if index <= len(wallet_addresses):
                    address = wallet_addresses[index - 1]
                    selected_addresses.append(address)
                    print(f"{index}: {address}")
                else:
                    logging.error(f"Індекс {index} перевищує кількість адрес у файлі")
        else:
            print("Порядкові номери гаманців не знайдено в конфігурації")
        
        if check_gwei(config, api_keys):
            balance = check_balance(api_keys)
            if balance:
                filtered_balance = filter_balance_data(balance)
                for entry in filtered_balance:
                    print(f"Currency: {entry['Currency']}, Available Balance: {entry['Available Balance']}, Equivalent in USD: {entry['Equivalent in USD']}")
                total_eq_usd = round(float(balance['data'][0]['totalEq']), 2)
                print(f"Total Equivalent in USD: {total_eq_usd}")

                eth_balance = next((item for item in balance['data'][0]['details'] if item['ccy'] == 'ETH'), None)
                if eth_balance and float(eth_balance['availBal']) >= float(config["amount"]):
                    for address in selected_addresses:
                        withdraw(config["amount"], address, config, api_keys)
                else:
                    print("Недостатньо коштів на балансі")
            else:
                print("Не вдалося отримати баланс")
        else:
            print("Виведення коштів заборонено через високе значення GWEI")

        # Оновлення кожні 60 секунд
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Непередбачена помилка: {str(e)}")
        print(f"Непередбачена помилка: {str(e)}")