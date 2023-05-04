from beem.blockchain import Blockchain
import json


def get_card_info(txid_index):
    tx_id = txid_index.split('-')
    index = int(tx_id[1])
    b = Blockchain()
    trans = b.get_transaction(tx_id[0])
    json_string = trans['operations'][0]['value']['json']
    cards_info = json.loads(json_string)

    if isinstance(cards_info, dict):
        return get_card_info(cards_info['ids'][0])

    return cards_info[0]['cards'][0], cards_info[0]['price']
