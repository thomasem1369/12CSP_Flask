from flask import Flask, request, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

@app.route('/')
def render_home():
    search_query = request.args.get('search')
    return render_template('index.html', search=search_query)

if __name__ == "__main__":
    app.run()
