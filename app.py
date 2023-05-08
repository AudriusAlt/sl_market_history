from flask import Flask, render_template, request, session, jsonify
import time
from bchain import get_card_info, get_market_history

exporting_threads = {}
app = Flask(__name__)
app.debug = True
app.secret_key = 'very_very_secret'
MAX_DAYS = 90
DEFAULT_DAYS = 30


@app.route('/count')
def get_count():
    return str(session.get('count', 0))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_time = time.time()

        username = request.form['username']
        try:
            days = int(request.form['days'])
        except ValueError:
            days = DEFAULT_DAYS
        if days > MAX_DAYS:
            days = MAX_DAYS
        rows = get_market_history(username, days)
        seconds = time.time() - start_time
        # Render the template with the data
        return render_template('history.html', rows=rows, username=username, days=days, seconds=seconds, count=len(rows))
    else:
        return render_template('index.html')
