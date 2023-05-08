from beem.blockchain import Blockchain
from beem.account import Account
from datetime import datetime, timedelta
import requests
import json


def get_card_info(txid_index):
    tx_id = txid_index.split('-')
    index = int(tx_id[-1])
    op = 0
    if len(tx_id) > 2:
        op = int(tx_id[1])
    b = Blockchain()
    trans = b.get_transaction(tx_id[0])
    json_string = trans['operations'][op]['value']['json']
    cards_info = json.loads(json_string)
    print('===================================')
    print(txid_index)
    print('***********************************')
    print(trans)
    print(';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;')
    print(cards_info)
    print('===================================')
    if isinstance(cards_info, dict):
        if "ids" in cards_info or "trx_ids" in cards_info:
            try:
                card_id, old_price = get_card_info(cards_info['ids'][index])
                new_price = cards_info['new_price']
                return card_id, new_price
            except KeyError:
                card_id, old_price = get_card_info(cards_info['trx_ids'][index])
                new_price = cards_info['new_price']
                return card_id, new_price
        else:
            try:
                price = float(cards_info['price'])
                card_id = cards_info['cards'][0]
            except ValueError:
                price = 0.0
                card_id = '-'
    else:
        try:
            price = float(cards_info[index]['price'])
            card_id = cards_info[index]['cards'][0]
        except ValueError:
            price = 0.0
            card_id = '-'

    return card_id, price


def get_market_history(username, days):
    url = 'https://api.splinterlands.io/transactions/lookup'
    card_lookup_url = 'https://api.splinterlands.io/cards/find'
    acc = Account(username)
    stop = datetime.utcnow() - timedelta(days=days)
    rows = []
    for tx in acc.history_reverse(stop=stop):
        if "id" in tx:
            if tx["id"] == "sm_market_purchase":
                params = {
                    'trx_id': tx["trx_id"]
                }
                response = requests.get(url, params=params).json()
                result_string = response['trx_info']['result']
                try:
                    result = json.loads(result_string)
                except TypeError:
                    continue
                by_seller = result["by_seller"]
                for seller in by_seller:
                    items = seller["items"]
                    for item in items:
                        card_number, price = get_card_info(item)
                        card_number_params = {'ids': card_number}
                        try:
                            card_details_response = requests.get(card_lookup_url, params=card_number_params).json()
                            card_name = card_details_response[0]["details"]["name"]
                        except requests.exceptions.JSONDecodeError:
                            print('Cant get card name for card number ' + card_number)
                            card_name = 'N/A'
                        rate = result['total_usd'] / result['total_dec']
                        try:
                            rows.append({
                                'date': datetime.strptime(response['trx_info']['created_date'],
                                                          "%Y-%m-%dT%H:%M:%S.000Z"),
                                'type': card_name,
                                'card': card_number,
                                'quantity': seller['seller'],
                                'price_usd': f"$ {price:,.3f}",
                                'price_dec': f"{(price / rate):,.3f} DEC",
                                'rate': f"{rate:.6f}"
                            })
                        except ValueError:
                            print('DEBUG price:' + price + ' card number ' + card_number)
                            continue
    return rows
