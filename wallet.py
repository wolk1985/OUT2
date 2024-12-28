import csv
import logging

def process_wallet_indexes(indexes):
    expanded_indexes = []
    for index in indexes:
        if isinstance(index, str) and '-' in index:
            start, end = map(int, index.split('-'))
            expanded_indexes.extend(range(start, end + 1))
        else:
            expanded_indexes.append(int(index))
    return expanded_indexes

def load_wallet_addresses(file_path):
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            wallet_addresses = [row[0] for row in reader]
        return wallet_addresses
    except Exception as e:
        logging.error(f"Помилка при читанні {file_path}: {str(e)}")
        raise