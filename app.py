"""Run the Flask application for the Vendor Management System."""

# Import Flask tools needed for the website
from flask import Flask, request, render_template
import sqlite3
from sqlite3 import Error

# Create the Flask application
app = Flask(__name__)
DATABASE = "vendor_management_system_3.db"


def create_connection(db_file):
    """Create a connnection to the database."""
    # Try to connect to the SQLite database
    try:
        connection = sqlite3.connect(db_file)

        # Allows us to access the columns by name instead of index
        connection.row_factory = sqlite3.Row

        return connection

    # Display an error if database connection fails
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_home():
    """Display the home page of the website."""
    # Display the homepage HTML file
    return render_template('index.html')


@app.route('/search')
def render_search():
    """Display the search results for businesses based on the search query."""
    # Get the search entered by the user from the URL
    search_query = request.args.get('search')

    # Connect to the database
    db = create_connection(DATABASE)
    cursor = db.cursor()

    # If no search was entered, show all businesses in alphabetical order
    if not search_query:
        cursor.execute("SELECT * FROM business ORDER BY business_name ASC")

    # Otherwise search and sort by match relevance, then alphabetically
    else:
        cursor.execute(
            # Trialled and chose Gemini's code over mine
            """
            SELECT * FROM business
            WHERE business_name LIKE ?
            ORDER BY
                CASE
                    -- Highest priority: Name starts with the query
                    WHEN business_name LIKE ? THEN 1
                    -- Lower priority: Contains the query anywhere else
                    ELSE 2
                END,
                business_name ASC
            """,
            (f"%{search_query}%", f"{search_query}%")
        )

    # Get the matching rows from the database
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    result = [dict(row) for row in rows]

    # Close the database connection
    db.close()

    # Send the search results and query string to the template
    return render_template('search.html', result=result,
                           search_query=search_query)


@app.route('/information_profile/<int:business_id>')
def render_information_profile(business_id):
    """Display the information profile for a specific business."""
    # Connect to the database
    db = create_connection(DATABASE)
    cursor = db.cursor()

    # Find the business using its uinque business ID
    cursor.execute("SELECT * FROM business WHERE business_id = ?",
                   (business_id,))

    # Get the business information
    business_row = cursor.fetchone()

    # Convert the business information into a dictionary
    business = dict(business_row) if business_row else None

    # Find all venfors connected to this business
    cursor.execute("SELECT v.vendor_name, v.contact_number FROM vendors v \
                    INNER JOIN business_vendors bv \
                    ON v.vendor_id = bv.vendor_id \
                    WHERE bv.business_id = ?", (business_id,))

    # Get the vendors from the database
    vendor_rows = cursor.fetchall()

    # Convert the vendor rows into a dictionaries
    vendors = [dict(row) for row in vendor_rows]

    # Find all locations connected to this business
    cursor.execute("SELECT l.location_name FROM locations l \
                    INNER JOIN business_locations bl \
                    ON l.location_id = bl.location_id \
                    WHERE bl.business_id = ?", (business_id,))

    # Grt the locations from the database
    location_rows = cursor.fetchall()

    # Convert the location rows into dictionaries
    locations = [dict(row) for row in location_rows]

    # Close the database connection
    db.close()

    # Send the business, vendor and location info to profile page
    return render_template('information_profile.html',
                           business=business, vendors=vendors,
                           locations=locations)


@app.route('/business_table')
def render_business_table():
    """Display the business table with search and sorting functionality."""
    # Get the business search value from the URL
    search_query = request.args.get('business_name')

    # Get the selected sorting option from the URL
    sort = request.args.get('sort')

    # Set the SQL sorting direction
    # name_desc sorts Z-A, otherwisee sorts A-Z
    if sort == "name_desc":
        order_sql = "ORDER BY b.business_name DESC"
    else:
        order_sql = "ORDER BY b.business_name ASC"

    # Connect to the database
    db = create_connection(DATABASE)
    cursor = db.cursor()

    # Show all businesses if no search value was entered
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

    # Otherwise show the business matching the search
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

    # Get the results from the database
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    result = [dict(row) for row in rows]

    # Close the database connection
    db.close()

    # Send the business table results to HTML page
    return render_template('business_table.html', result=result)


@app.route('/locations_table')
def render_locations_table():
    """Display the locations table with search and sorting functionality."""
    # Get the location search valye from the URL
    search_query = request.args.get('search')

    # Get the selected sorting option from the URL
    sort = request.args.get('sort')

    # Set the SQL sorting direction
    # name_desc sorts Z-A, otherwisee sorts A-Z
    if sort == "name_desc":
        order_sql = "ORDER BY b.business_name DESC"
    else:
        order_sql = "ORDER BY b.business_name ASC"

    # Connect to the database
    db = create_connection(DATABASE)
    cursor = db.cursor()

    # Get all locations from the locations table
    cursor.execute("SELECT * FROM locations;")
    rows = cursor.fetchall()

    # Convert the location rows into dictionaries
    locations = [dict(row) for row in rows]

    # Show all businesses if no search value was entered
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

    # Otherwise search for the selected business
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

    # Get the results from the database
    rows = cursor.fetchall()

    # Convert the rows into dictionaries
    result = [dict(row) for row in rows]

    # Close the database connection
    db.close()

    # Send the results to the locations HTML page
    return render_template('locations_table.html',
                           result=result, locations=locations)


# Run the Flask application
if __name__ == "__main__":
    app.run()
