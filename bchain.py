from beem.blockchain import Blockchain
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

    if isinstance(cards_info, dict):
        try:
            card_id, old_price = get_card_info(cards_info['ids'][index])
            new_price = cards_info['new_price']
            return card_id, new_price
        except KeyError:
            card_id, old_price = get_card_info(cards_info['trx_ids'][index])
            new_price = cards_info['new_price']
            return card_id, new_price

    try:
        price = float(cards_info[index]['price'])
    except ValueError:
        price = 0.0

    return cards_info[index]['cards'][0], price
