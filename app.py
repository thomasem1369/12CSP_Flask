from flask import Flask, request, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
DATABASE = "vendor_management_system.db"

def create_connection(db_file):
    """Creates a connnection to the database"""

    try:
        connection = sqlite3.connect(db_file)
        connection.row_factory = sqlite3.Row
        return connection
    except Error as e:
        print(e)
    return None

@app.route('/')
def render_home():
    return render_template('index.html')

@app.route('/search')
def render_search():
    search_query = request.args.get('search')
    db =  create_connection(DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * from business WHERE business_name = ?", (search_query,))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    print(result)
    db.close()
    return render_template('search.html', result=result)

@app.route('/add_business')
def render_add_business():
    return render_template('add_business.html')

@app.route('/add_vendor')
def render_add_vendor():
    return render_template('add_vendor.html')

@app.route('/link_business_vendor')
def render_link_business_vendor():
    return render_template('link_business_vendor.html')

@app.route('/business_table')
def render_business_table():   
    return render_template('business_table.html')

@app.route('/vendor_table')
def render_vendor_table():
    return render_template('vendor_table.html')

@app.route('/locations_table')
def render_locations_table():
    return render_template('locations_table.html') 


if __name__ == "__main__":
    app.run()
