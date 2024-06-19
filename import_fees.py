import requests
import csv
from datetime import datetime
import pytz

def fetch_transactions(address):
    url = f'https://block-explorer-api.mainnet.zksync.io/api?module=account&action=txlist&page=1&offset=100&sort=desc&endblock=99999999&startblock=0&address={address}'
    headers = {'accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1':
            return data['result']
        else:
            print(f"API Error: {data['message']}")
    else:
        print(f"HTTP Error: {response.status_code}")
    
    return []

def convert_timestamp_to_date(timestamp, timezone='Europe/Rome'):
    tz = pytz.timezone(timezone)
    dt_object = datetime.fromtimestamp(int(timestamp), tz)
    # Manually format day and month to remove leading zeroes
    formatted_date = dt_object.strftime(f'{dt_object.day}/{dt_object.month}/%Y, %H:%M:%S')
    return formatted_date

def generate_csv(transactions, filename='fees.csv', timezone='Europe/Rome'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Amount', 'Token Symbol', 'Type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for tx in transactions:
            writer.writerow({
                'Date': convert_timestamp_to_date(tx['timeStamp'], timezone),
                'Amount': str(int(tx['fee']) / 10**18),
                'Token Symbol': 'ETH',
                'Type': 'fee'
            })

def merge_csv_files(transactions_file='transazioni.csv', fees_file='fees.csv', output_file='transactions_and_fees.csv'):
    with open(transactions_file, 'r', newline='') as trans_file, \
         open(fees_file, 'r', newline='') as fees_file, \
         open(output_file, 'w', newline='') as out_file:
        
        trans_reader = csv.DictReader(trans_file)
        fees_reader = csv.DictReader(fees_file)
        fieldnames = trans_reader.fieldnames
        
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in trans_reader:
            writer.writerow(row)
        #Se dà errore ValueError: dict contains fields not in fieldnames: 'Date', aprire il file transazioni.csv in vs code e in basso a destra cambiare l'encoding in utf-8 "save with encoding"
        for row in fees_reader:
            writer.writerow({
                'Date': row['Date'],
                'Amount': row['Amount'],
                'Token symbol': row['Token Symbol'],
                'Type': row['Type'],
                'Direction': '',
                'From': '',
                'From origin': '',
                'To': '',
                'To origin': '',
                'Token L1 address': '',
                'Token L2 address': '',
                'Transaction hash': ''
            })


def main():
    address = '0x4563cE46D857ca9d7c30fe1729dEA71555CBf6B9'  # Replace with the desired address
    transactions = fetch_transactions(address)
    generate_csv(transactions, timezone='Europe/Rome')
    merge_csv_files(transactions_file='transazioni.csv', fees_file='fees.csv', output_file='transactions_and_fees.csv')

if __name__ == "__main__":
    main()
