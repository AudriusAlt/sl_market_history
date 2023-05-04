from flask import Flask, render_template
from beem.account import Account
from datetime import datetime, timedelta
import requests
import json
from bchain import get_card_info


app = Flask(__name__)


@app.route('/')
def index():
    # Fetch the HTML data from the page
    url = 'https://api.splinterlands.io/transactions/lookup'
    acc = Account("altas")

    # Parse the HTML using BeautifulSoup

    # Find the table element containing the data


    # Extract the data from the table

    stop = datetime.utcnow() - timedelta(days=30)
    rows = []
    for tx in acc.history_reverse(stop=stop):
        if "id" in tx:
            if tx["id"] == "sm_market_purchase":
                params = {
                    'trx_id': tx["trx_id"]
                }
                response = requests.get(url, params=params).json()
                result_string = response['trx_info']['result']

                result = json.loads(result_string)
                by_seller = result["by_seller"]
                for seller in by_seller:
                    items = seller["items"]
                    for item in items:
                        print('********************')
                        print(result_string)
                        print('********************')
                        card_number, price = get_card_info(item)
                        rate = result['total_usd'] / result['total_dec']
                        rows.append({
                            'date': response['trx_info']['created_date'],
                            'type': response['trx_info']['type'],
                            'card': card_number,
                            'quantity': seller['seller'],
                            'price_usd': price,
                            'price_dec': price / rate
                        })








    # Render the template with the data
    return render_template('index.html', rows=rows)

