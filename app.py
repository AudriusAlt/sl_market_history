from flask import Flask, render_template, request
from beem.account import Account
from datetime import datetime, timedelta
import requests
import json
from bchain import get_card_info

app = Flask(__name__)
MAX_DAYS = 90
DEFAULT_DAYS = 30


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = 'https://api.splinterlands.io/transactions/lookup'
        card_lookup_url = 'https://api.splinterlands.io/cards/find'
        username = request.form['username']
        try:
            days = int(request.form['days'])
        except ValueError:
            days = DEFAULT_DAYS
        if days > MAX_DAYS:
            days = MAX_DAYS
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

                    result = json.loads(result_string)
                    by_seller = result["by_seller"]
                    for seller in by_seller:
                        items = seller["items"]
                        for item in items:
                            card_number, price = get_card_info(item)
                            card_number_params = {'ids': card_number}
                            card_details_response = requests.get(card_lookup_url, params=card_number_params).json()
                            rate = result['total_usd'] / result['total_dec']
                            rows.append({
                                'date': datetime.strptime(response['trx_info']['created_date'], "%Y-%m-%dT%H:%M:%S.000Z"),
                                'type': card_details_response[0]["details"]["name"],
                                'card': card_number,
                                'quantity': seller['seller'],
                                'price_usd': f"$ {price:,.3f}",
                                'price_dec': f"{(price / rate):,.3f} DEC",
                                'rate': f"{rate:.6f}"
                            })

        # Render the template with the data
        return render_template('history.html', rows=rows, username=username, days=days)
    else:
        return render_template('index.html')
