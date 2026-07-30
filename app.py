from flask import Flask, request, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
DATABASE = "vendor_management_system.db"

def create_connection(db_file):
    """Creates a connnection to the database"""

    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None

@app.route('/')
def render_home():
    search_query = request.args.get('search')
    return render_template('index.html', search=search_query)


if __name__ == "__main__":
    app.run()
