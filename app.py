from flask import Flask, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

@app.route('/')
def render_home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
