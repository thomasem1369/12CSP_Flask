"""Run the Flask application for the Vendor Management System."""

from flask import Flask, request, render_template
import sqlite3
from sqlite3 import Error


app = Flask(__name__)
DATABASE = "vendor_management_system_3.db"


def create_connection(db_file):
    """Create a connnection to the database."""
    try:
        connection = sqlite3.connect(db_file)
        connection.row_factory = sqlite3.Row
        # Allows us to access the columns by name instead of index
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_home():
    """Display the home page of the website."""
    return render_template('index.html')


@app.route('/search')
def render_search():
    """Display the search results for businesses based on the search query."""
    search_query = request.args.get('search')

    db = create_connection(DATABASE)
    cursor = db.cursor()
    if not search_query:
        cursor.execute("SELECT * FROM business ORDER BY business_name ASC")
    else:
        cursor.execute(
            "SELECT * FROM business WHERE business_name LIKE ? "
            "ORDER BY business_name ASC",
            (f"%{search_query}%",))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    # Convert rows to a list of dictionaries instead of numbers
    db.close()
    return render_template('search.html', result=result)


@app.route('/information_profile/<int:business_id>')
def render_information_profile(business_id):
    """Display the information profile for a specific business."""
    db = create_connection(DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM business WHERE business_id = ?",
                   (business_id,))
    business_row = cursor.fetchone()
    business = dict(business_row) if business_row else None
    cursor.execute("SELECT v.vendor_name, v.contact_number FROM vendors v \
                    INNER JOIN business_vendors bv \
                    ON v.vendor_id = bv.vendor_id \
                    WHERE bv.business_id = ?", (business_id,))
    vendor_rows = cursor.fetchall()
    vendors = [dict(row) for row in vendor_rows]
    cursor.execute("SELECT l.location_name FROM locations l \
                    INNER JOIN business_locations bl \
                    ON l.location_id = bl.location_id \
                    WHERE bl.business_id = ?", (business_id,))
    location_rows = cursor.fetchall()
    locations = [dict(row) for row in location_rows]
    db.close()
    return render_template('information_profile.html',
                           business=business, vendors=vendors,
                           locations=locations)


@app.route('/business_table')
def render_business_table():
    """Display the business table with search and sorting functionality."""
    search_query = request.args.get('business_name')
    sort = request.args.get('sort')

    # Match and link the HTML query parameter values
    if sort == "name_desc":
        order_sql = "ORDER BY b.business_name DESC"
    else:
        order_sql = "ORDER BY b.business_name ASC"
    db = create_connection(DATABASE)
    cursor = db.cursor()
    # Show all if no search query filter
    if not search_query:
        cursor.execute(f"SELECT b.*, STRING_AGG(v.vendor_name, ', ') \
                as vendor_names, \
                STRING_AGG(v.contact_number, ', ') as contact_numbers \
                FROM business b \
                INNER JOIN business_vendors bv \
                ON b.business_id = bv.business_id \
                INNER JOIN vendors v ON v.vendor_id = bv.vendor_id \
                GROUP BY b.business_id \
                {order_sql}")
    else:
        cursor.execute(f"SELECT b.*, STRING_AGG(v.vendor_name, ', ') \
                    as vendor_names, \
                    STRING_AGG(v.contact_number, ', ') as contact_numbers \
                    FROM business b \
                    INNER JOIN business_vendors bv \
                    ON b.business_id = bv.business_id \
                    INNER JOIN vendors v ON v.vendor_id = bv.vendor_id \
                    GROUP BY b.business_id \
                    WHERE business_name = ? \
                    {order_sql}", (search_query,))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    # Convert rows to a list of dictionaries instead of numbers
    db.close()
    return render_template('business_table.html', result=result)


@app.route('/locations_table')
def render_locations_table():
    """Display the locations table with search and sorting functionality."""
    search_query = request.args.get('search')
    sort = request.args.get('sort')
    # Match and linkthe HTML query parameter values
    if sort == "name_desc":
        order_sql = "ORDER BY b.business_name DESC"
    else:
        order_sql = "ORDER BY b.business_name ASC"
    db = create_connection(DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM locations;")
    rows = cursor.fetchall()
    locations = [dict(row) for row in rows]
    # Convert rows to a list of dictionaries instead of numbers
    # Show all if no search query filter
    if not search_query:
        cursor.execute(f"SELECT b.business_id, b.business_name, \
                STRING_AGG(l.location_name, ', ') AS location_names \
                FROM business b \
                INNER JOIN business_locations bl \
                ON b.business_id = bl.business_id \
                INNER JOIN locations l \
                ON l.location_id = bl.location_id \
                GROUP BY b.business_id, b.business_name \
                {order_sql}")
    else:
        cursor.execute(f"SELECT b.business_id, b.business_name, \
                    STRING_AGG(l.location_name, ', ') AS location_names \
                    FROM business b \
                    INNER JOIN business_locations bl \
                    ON b.business_id = bl.business_id \
                    INNER JOIN locations l \
                    ON l.location_id = bl.location_id \
                    GROUP BY b.business_id, b.business_name; \
                    WHERE business_name = ? \
                    {order_sql}", (search_query,))

    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    # Convert rows to a list of dictionaries instead of numbers
    db.close()
    return render_template('locations_table.html',
                           result=result, locations=locations)


if __name__ == "__main__":
    app.run()
