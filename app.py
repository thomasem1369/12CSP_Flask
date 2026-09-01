from flask import Flask, request, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
DATABASE = "vendor_management_system.db"

def create_connection(db_file):
    """Creates a connnection to the database"""

    try:
        connection = sqlite3.connect(db_file)
        connection.row_factory = sqlite3.Row # This allows us to access the columns by name instead of index
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
    result = [dict(row) for row in rows] # Convert rows to a list of dictionaries instead of numbers
    print(result)
    db.close()
    return render_template('search.html', result=result)

@app.route('/business_table')
def render_business_table():   
    search_query = request.args.get('business_name')
    sort = request.args.get('sort')
    order = request.args.get('order')
    db =  create_connection(DATABASE)
    cursor = db.cursor()
    # Show all if no search query filter
    if not search_query:
        cursor.execute("SELECT b.*, STRING_AGG(v.vendor_name, ', ') as vendor_names, \
                STRING_AGG(v.contact_number, ', ') as contact_numbers \
                FROM business b \
                INNER JOIN business_vendors bv ON b.business_id = bv.business_id \
                INNER JOIN vendors v ON v.vendor_id = bv.vendor_id \
                GROUP BY b.business_id")
    else:
        cursor.execute("SELECT b.*, STRING_AGG(v.vendor_name, ', ') as vendor_names, \
                    STRING_AGG(v.contact_number, ', ') as contact_numbers \
                    FROM business b \
                    INNER JOIN business_vendors bv ON b.business_id = bv.business_id \
                    INNER JOIN vendors v ON v.vendor_id = bv.vendor_id \
                    GROUP BY b.business_id \
                    WHERE business_name = ?", (search_query,))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows] # Convert rows to a list of dictionaries instead of numbers
    #print(result)
    db.close()
    return render_template('business_table.html', result=result)


@app.route('/vendor_table')
def render_vendor_table():
    search_query = request.args.get('search')
    db =  create_connection(DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * from business WHERE business_name = ?", (search_query,))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows] # Convert rows to a list of dictionaries instead of numbers
    print(result)
    db.close()
    return render_template('vendor_table.html')

@app.route('/locations_table')
def render_locations_table():
    search_query = request.args.get('search')
    db =  create_connection(DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * from business WHERE business_name = ?", (search_query,))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows] # Convert rows to a list of dictionaries instead of numbers
    print(result)
    db.close()
    return render_template('locations_table.html') 


if __name__ == "__main__":
    app.run()
